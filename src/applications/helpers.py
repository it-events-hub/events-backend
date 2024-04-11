from .models import Application, NotificationSettings
from api.loggers import logger
from events.models import Event
from users.models import User


def create_notification_settings(
    user: User | None = None, application: Application | None = None
) -> None:
    """Creates notification settings object linked to the user or to the application."""
    NotificationSettings.objects.create(user=user, application=application)
    logger.debug(
        f"Notification settings for user {user}, application {application} were added."
    )


class EventClosureController:
    """
    Checks participant limits for an event after submitting an application
    to participate in that event and closes registration for the event entirely
    or partially (offline, online) if the limits are reached.
    """

    @staticmethod
    def check_offline_event_limit(event: Event) -> bool:
        """Checks if the participant limit for the offline event is reached."""
        return (
            event.format == Event.FORMAT_OFFLINE
            and event.participant_offline_limit
            and event.applications.filter(format=Event.FORMAT_OFFLINE).count()
            >= event.participant_offline_limit
        )

    @staticmethod
    def check_online_event_limit(event: Event) -> bool:
        """Checks if the participant limit for the online event is reached."""
        return (
            event.format == Event.FORMAT_ONLINE
            and event.participant_online_limit
            and event.applications.filter(format=Event.FORMAT_ONLINE).count()
            >= event.participant_online_limit
        )

    @staticmethod
    def check_hybrid_event_offline_reached_online_not(event: Event) -> bool:
        """
        Checks that the offline participant limit has been reached and
        the online participant limit has not been reached.
        """
        offline_limit_reached: bool = (
            event.format == Event.FORMAT_HYBRID
            and event.participant_offline_limit
            and event.applications.filter(format=Event.FORMAT_OFFLINE).count()
            >= event.participant_offline_limit
        )
        online_limit_not_reached: bool = (
            not event.participant_online_limit
            or event.applications.filter(format=Event.FORMAT_ONLINE).count()
            < event.participant_online_limit
        )
        return offline_limit_reached and online_limit_not_reached

    @staticmethod
    def check_hybrid_event_online_reached_offline_not(event: Event) -> bool:
        """
        Checks that the online participant limit has been reached and
        the offline participant limit has not been reached.
        """
        online_limit_reached: bool = (
            event.format == Event.FORMAT_HYBRID
            and event.participant_online_limit
            and event.applications.filter(format=Event.FORMAT_ONLINE).count()
            >= event.participant_online_limit
        )
        offline_limit_not_reached: bool = (
            not event.participant_offline_limit
            or event.applications.filter(format=Event.FORMAT_OFFLINE).count()
            < event.participant_offline_limit
        )
        return online_limit_reached and offline_limit_not_reached

    @staticmethod
    def check_hybrid_event_offline_limit(event: Event) -> bool:
        """Checks if the participant offline limit for the hybrid event is reached."""
        return (
            event.format == Event.FORMAT_HYBRID
            and event.participant_offline_limit
            and event.applications.filter(format=Event.FORMAT_OFFLINE).count()
            >= event.participant_offline_limit
        )

    @staticmethod
    def check_hybrid_event_online_limit(event: Event) -> bool:
        """Checks if the participant online limit for the hybrid event is reached."""
        return (
            event.format == Event.FORMAT_HYBRID
            and event.participant_online_limit
            and event.applications.filter(format=Event.FORMAT_ONLINE).count()
            >= event.participant_online_limit
        )

    @staticmethod
    def check_event_limits_and_close_registration(event: Event) -> None:
        """
        Checks event participant limits and closes registration if limits are reached.
        """
        previous_event_status: str = event.status
        if EventClosureController.check_hybrid_event_offline_reached_online_not(event):
            event.status = Event.STATUS_OFFLINE_CLOSED
        elif EventClosureController.check_hybrid_event_online_reached_offline_not(
            event
        ):
            event.status = Event.STATUS_ONLINE_CLOSED
        elif (
            EventClosureController.check_offline_event_limit(event)
            or EventClosureController.check_online_event_limit(event)
            or (
                event.status == Event.STATUS_OFFLINE_CLOSED
                and EventClosureController.check_hybrid_event_online_limit(event)
            )
            or (
                event.status == Event.STATUS_ONLINE_CLOSED
                and EventClosureController.check_hybrid_event_offline_limit(event)
            )
        ):
            event.status = Event.STATUS_CLOSED
        event.save()
        if event.status != previous_event_status:
            logger.debug(f"The status of event {event} was changed to {event.status}")


# TODO: вынести весь блок методов, открывающих регистрацию, в отдельный файл, logger

# NO CHANGE ситуация 1: статус ивента "регистрация открыта", тогда не меняем статус

# OPEN ситуация 2: ивент имеет строгий формат и статус был "регистрация закрыта",
# тогда после отмены заявки меняем статус ивента на "регистрация открыта"

# ситуация 3: ивент имеет гибридный формат и статус "регистрация закрыта", тогда
# нужно посмотреть, какие лимиты имеет этот ивент (у него может не быть какого-то
# типа лимита, ведь эти поля необязательные) и какой формат был у отмененной заявки:

# 3.1 если у ивента были оба лимита и заявка была офлайн, тогда меняем статус ивента
# на "регистрация онлайн закрыта" (то есть возобновляем офлайн-регистрацию)
# 3.2 если у ивента были оба лимита и заявка была онлайн, тогда меняем статус ивента
# на "регистрация офлайн закрыта" (то есть возобновляем онлайн-регистрацию)
# 3.3 OPEN если у ивента был только офлайн-лимит и заявка была офлайн, то меняем
# статус на "регистрация открыта"
# 3.4 OPEN если у ивента был только онлайн-лимит и заявка была онлайн, то меняем
# статус на "регистрация открыта"
# 3.5 NO CHANGE если у ивента был только офлайн-лимит, а заявка была онлайн, то
# не меняем статус
# 3.6 NO CHANGE если у ивента был только онлайн-лимит, а заявка была офлайн, то
# не меняем статус
# 3.7 NO CHANGE если у ивента не было лимитов, то у него и статус должен был
# оставаться "регистрация открыта", но если админ в Админке вручную поменял статус
# на "регистрация закрыта", а потом кто-то отменил заявку, то не меняем статус
# ивента автоматически, пусть админ и дальше осуществляет ручное управление статусом
# ивента, раз он уже начал вмешиваться в автоматическую смену статусов

# ситуация 4: ивент имеет гибридный формат, офлайн-лимит и статус "регистрация
# офлайн закрыта":
# 4.1 OPEN заявка была офлайн, тогда меняем статус ивента на "регистрация открыта"
# 4.2 NO CHANGE заявка была онлайн, тогда не меняем статус ивента

# ситуация 5: ивент имеет гибридный формат, онлайн-лимит и статус "регистрация
# онлайн закрыта":
# 5.1 OPEN заявка была онлайн, тогда меняем статус ивента на "регистрация открыта"
# 5.2 NO CHANGE заявка была офлайн, тогда не меняем статус ивента

# TODO: add logging (event status changes)


class EventReopeningController:
    """
    Checks participant limits for an event after the deletion of an application
    and reopens registration for the event entirely or partially (offline, online),
    if applicable.
    """

    @staticmethod
    def check_event_limits_and_reopen_registration(
        event: Event, application_format: str
    ) -> None:
        """Checks event participant limits and reopens registration if applicable."""
        previous_event_status: str = event.status

        closed_strict_format_event: bool = (
            event.format != Event.FORMAT_HYBRID and event.status == Event.STATUS_CLOSED
        )
        hybrid_event_closed_offline_and_application_offline: bool = (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_OFFLINE_CLOSED
            and event.participant_offline_limit
            and application_format == Event.FORMAT_OFFLINE
        )
        hybrid_event_closed_online_and_application_online: bool = (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_ONLINE_CLOSED
            and event.participant_online_limit
            and application_format == Event.FORMAT_ONLINE
        )
        closed_hybrid_event_had_only_offline_limit_and_application_offline: bool = (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_CLOSED
            and event.participant_offline_limit
            and not event.participant_online_limit
            and application_format == Event.FORMAT_OFFLINE
        )
        closed_hybrid_event_had_only_online_limit_and_application_online: bool = (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_CLOSED
            and not event.participant_offline_limit
            and event.participant_online_limit
            and application_format == Event.FORMAT_ONLINE
        )
        closed_hybrid_event_had_both_limits_and_application_online: bool = (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_CLOSED
            and event.participant_offline_limit
            and event.participant_online_limit
            and application_format == Event.FORMAT_ONLINE
        )
        closed_hybrid_event_had_both_limits_and_application_offline: bool = (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_CLOSED
            and event.participant_offline_limit
            and event.participant_online_limit
            and application_format == Event.FORMAT_OFFLINE
        )

        if (
            closed_strict_format_event
            or hybrid_event_closed_offline_and_application_offline
            or hybrid_event_closed_online_and_application_online
            or closed_hybrid_event_had_only_offline_limit_and_application_offline
            or closed_hybrid_event_had_only_online_limit_and_application_online
        ):
            event.status = Event.STATUS_OPEN

        elif closed_hybrid_event_had_both_limits_and_application_online:
            event.status = Event.STATUS_OFFLINE_CLOSED

        elif closed_hybrid_event_had_both_limits_and_application_offline:
            event.status = Event.STATUS_ONLINE_CLOSED

        event.save()
        if event.status != previous_event_status:
            logger.debug(f"The status of event {event} was changed to {event.status}")

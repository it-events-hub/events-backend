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
    def check_event_limits_and_close_registration(event: Event) -> None:
        """
        Checks event participant limits and closes registration if limits are reached.
        """
        previous_event_status: str = event.status

        if EventClosureController._hybrid_event_offline_limit_reached_online_limit_not(
            event
        ):
            event.status = Event.STATUS_OFFLINE_CLOSED

        elif (
            EventClosureController._hybrid_event_online_limit_reached_offline_limit_not(
                event
            )
        ):
            event.status = Event.STATUS_ONLINE_CLOSED

        elif (
            EventClosureController._offline_event_limit_reached(event)
            or EventClosureController._online_event_limit_reached(event)
            or (
                event.status == Event.STATUS_OFFLINE_CLOSED
                and EventClosureController._hybrid_event_online_limit_reached(event)
            )
            or (
                event.status == Event.STATUS_ONLINE_CLOSED
                and EventClosureController._hybrid_event_offline_limit_reached(event)
            )
        ):
            event.status = Event.STATUS_CLOSED

        event.save()

        if event.status != previous_event_status:
            logger.debug(f"The status of event {event} was changed to {event.status}")

    @staticmethod
    def _offline_event_limit_reached(event: Event) -> bool:
        """Checks if the participant limit for the offline event is reached."""
        return (
            event.format == Event.FORMAT_OFFLINE
            and event.participant_offline_limit
            and event.applications.filter(format=Event.FORMAT_OFFLINE).count()
            >= event.participant_offline_limit
        )

    @staticmethod
    def _online_event_limit_reached(event: Event) -> bool:
        """Checks if the participant limit for the online event is reached."""
        return (
            event.format == Event.FORMAT_ONLINE
            and event.participant_online_limit
            and event.applications.filter(format=Event.FORMAT_ONLINE).count()
            >= event.participant_online_limit
        )

    @staticmethod
    def _hybrid_event_offline_limit_reached_online_limit_not(event: Event) -> bool:
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
    def _hybrid_event_online_limit_reached_offline_limit_not(event: Event) -> bool:
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
    def _hybrid_event_offline_limit_reached(event: Event) -> bool:
        """Checks if the participant offline limit for the hybrid event is reached."""
        return (
            event.format == Event.FORMAT_HYBRID
            and event.participant_offline_limit
            and event.applications.filter(format=Event.FORMAT_OFFLINE).count()
            >= event.participant_offline_limit
        )

    @staticmethod
    def _hybrid_event_online_limit_reached(event: Event) -> bool:
        """Checks if the participant online limit for the hybrid event is reached."""
        return (
            event.format == Event.FORMAT_HYBRID
            and event.participant_online_limit
            and event.applications.filter(format=Event.FORMAT_ONLINE).count()
            >= event.participant_online_limit
        )


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

        if (
            EventReopeningController._reopen_closed_event_of_strict_format(event)
            or EventReopeningController._reopen_offline_closed_hybrid_event(
                event, application_format
            )
            or EventReopeningController._reopen_online_closed_hybrid_event(
                event, application_format
            )
            or EventReopeningController._reopen_hybrid_event_with_only_offline_limit(
                event, application_format
            )
            or EventReopeningController._reopen_hybrid_event_with_only_online_limit(
                event, application_format
            )
        ):
            event.status = Event.STATUS_OPEN

        elif EventReopeningController._online_reopen_hybrid_event_with_both_limits(
            event, application_format
        ):
            event.status = Event.STATUS_OFFLINE_CLOSED

        elif EventReopeningController._offline_reopen_hybrid_event_with_both_limits(
            event, application_format
        ):
            event.status = Event.STATUS_ONLINE_CLOSED

        event.save()

        if event.status != previous_event_status:
            logger.debug(f"The status of event {event} was changed to {event.status}")

    @staticmethod
    def _reopen_closed_event_of_strict_format(event: Event) -> bool:
        """
        Checks if fully closed event with strict (not hybrid) format should fully reopen
        after cancellation of any application.
        """
        return (
            event.format != Event.FORMAT_HYBRID and event.status == Event.STATUS_CLOSED
        )

    @staticmethod
    def _reopen_offline_closed_hybrid_event(
        event: Event, application_format: str
    ) -> bool:
        """
        Checks if hybrid event, which was closed offline and had participant offline
        limit, should fully reopen after cancellation of offline application.
        """
        return (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_OFFLINE_CLOSED
            and event.participant_offline_limit
            and application_format == Event.FORMAT_OFFLINE
        )

    @staticmethod
    def _reopen_online_closed_hybrid_event(
        event: Event, application_format: str
    ) -> bool:
        """
        Checks if hybrid event, which was closed online and had participant online
        limit, should fully reopen after cancellation of online application.
        """
        return (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_ONLINE_CLOSED
            and event.participant_online_limit
            and application_format == Event.FORMAT_ONLINE
        )

    @staticmethod
    def _reopen_hybrid_event_with_only_offline_limit(
        event: Event, application_format: str
    ) -> bool:
        """
        Checks if hybrid event, which was fully closed and had only participant offline
        limit, should fully reopen after cancellation of offline application.
        """
        return (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_CLOSED
            and event.participant_offline_limit
            and not event.participant_online_limit
            and application_format == Event.FORMAT_OFFLINE
        )

    @staticmethod
    def _reopen_hybrid_event_with_only_online_limit(
        event: Event, application_format: str
    ) -> bool:
        """
        Checks if hybrid event, which was fully closed and had only participant online
        limit, should fully reopen after cancellation of online application.
        """
        return (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_CLOSED
            and not event.participant_offline_limit
            and event.participant_online_limit
            and application_format == Event.FORMAT_ONLINE
        )

    @staticmethod
    def _online_reopen_hybrid_event_with_both_limits(
        event: Event, application_format: str
    ) -> bool:
        """
        Checks if hybrid event, which was fully closed and had both (offline and online)
        participant limits, should reopen for online applications after cancellation of
        online application.
        """
        return (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_CLOSED
            and event.participant_offline_limit
            and event.participant_online_limit
            and application_format == Event.FORMAT_ONLINE
        )

    @staticmethod
    def _offline_reopen_hybrid_event_with_both_limits(
        event: Event, application_format: str
    ) -> bool:
        """
        Checks if hybrid event, which was fully closed and had both (offline and online)
        participant limits, should reopen for offline applications after cancellation of
        offline application.
        """
        return (
            event.format == Event.FORMAT_HYBRID
            and event.status == Event.STATUS_CLOSED
            and event.participant_offline_limit
            and event.participant_online_limit
            and application_format == Event.FORMAT_OFFLINE
        )

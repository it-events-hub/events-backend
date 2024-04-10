from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from .models import Application, NotificationSettings
from .serializers import (
    ApplicationCreateAnonymousSerializer,
    ApplicationCreateAuthorizedSerializer,
    NotificationSettingsSerializer,
)
from .utils_db_write import create_notification_settings
from api.loggers import logger
from api.permissions import IsAuthorOrCreateOnly
from events.models import Event
from users.models import Specialization


# TODO: Если заявка отменена авторизованным юзером, то открывать регистрацию снова.
# TODO: Возвращать статус 200 и response body в случае удаления объекта
class ApplicationViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    """ViewSet to create and delete applications for participation in events."""

    queryset = Application.objects.all()
    permission_classes = [IsAuthorOrCreateOnly]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return ApplicationCreateAuthorizedSerializer
        return ApplicationCreateAnonymousSerializer

    @staticmethod
    def update_authenticated_user_personal_data(
        user: SimpleLazyObject, validated_data: list[Any]
    ) -> None:
        """
        Updates personal data if authenticated user change this data in the application.
        """
        user_validated_data: list[Any] = {
            "first_name": validated_data.get("first_name"),
            "last_name": validated_data.get("last_name"),
            "email": validated_data.get("email"),
            "phone": validated_data.get("phone"),
            "telegram": validated_data.get("telegram"),
            "birth_date": validated_data.get("birth_date"),
            "city": validated_data.get("city"),
            "activity": validated_data.get("activity"),
            "company": validated_data.get("company"),
            "position": validated_data.get("position"),
            "experience_years": validated_data.get("experience_years"),
        }
        specializations: list[Specialization] = validated_data.get("specializations")
        if any(user_validated_data):
            for key, value in user_validated_data.items():
                if value:
                    setattr(user, key, value)
                    logger.debug(
                        f"The {key} of {user} was updated, new value: {value}."
                    )
        if specializations:
            user.specializations.set(specializations)
            logger.debug(
                f"The specializations of {user} were updated, new specializations: "
                f"{specializations}."
            )
        user.save()

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
        if ApplicationViewSet.check_hybrid_event_offline_limit(event):
            event.status = Event.STATUS_OFFLINE_CLOSED
            logger.debug(
                f"The status of event {event} was changed to "
                f"{Event.STATUS_OFFLINE_CLOSED}"
            )
        elif ApplicationViewSet.check_hybrid_event_online_limit(event):
            event.status = Event.STATUS_ONLINE_CLOSED
            logger.debug(
                f"The status of event {event} was changed to "
                f"{Event.STATUS_ONLINE_CLOSED}"
            )
        elif (
            ApplicationViewSet.check_offline_event_limit(event)
            or ApplicationViewSet.check_online_event_limit(event)
            or (
                event.status == Event.STATUS_OFFLINE_CLOSED
                and ApplicationViewSet.check_hybrid_event_online_limit(event)
            )
            or (
                event.status == Event.STATUS_ONLINE_CLOSED
                and ApplicationViewSet.check_hybrid_event_offline_limit(event)
            )
        ):
            event.status = Event.STATUS_CLOSED
            logger.debug(
                f"The status of event {event} was changed to {Event.STATUS_CLOSED}"
            )
        event.save()

    def perform_create(self, serializer):
        """
        Adds the user to the application if the request user is authenticated.
        Triggers the authenticated user personal data update if the authenticated user
        change personal data in the application.
        Authomatically fills in the fields of an application of the authenticated user.
        Triggers creation of notification settings object if the user is anonymous.
        Triggers event participant limits checking and closure of registration
        if the limits are reached.
        """
        user: SimpleLazyObject | AnonymousUser = self.request.user
        if user.is_authenticated:
            ApplicationViewSet.update_authenticated_user_personal_data(
                user, serializer.validated_data
            )
            serializer.save(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=user.phone,
                telegram=user.telegram,
                birth_date=user.birth_date,
                city=user.city,
                activity=user.activity,
                company=user.company,
                position=user.position,
                experience_years=user.experience_years,
                specializations=user.specializations.all(),
            )
            event = serializer.validated_data["event"]
            logger.debug(
                f"The fields of the application submitted by an authorized user {user} "
                f"to participate in the event {event} were automatically filled in "
                "based on profile data"
            )
        else:
            serializer.save()
            created_application = serializer.instance
            create_notification_settings(application=created_application)
        ApplicationViewSet.check_event_limits_and_close_registration(
            serializer.validated_data["event"]
        )

    # TODO: отменить заявку может только авторизованный (на входе в эндпойнт удаления
    # стоит проверка в permission, наверно здесь можно дополнительно не проверять, что
    # юзер авторизован);

    # ситуация 1: статус ивента "регистрация открыта", тогда не меняем статус ивента

    # DONE ситуация 2: ивент имеет строгий формат и статус был "регистрация закрыта",
    # тогда после отмены заявки меняем статус ивента на "регистрация открыта"

    # ситуация 3: ивент имеет гибридный формат и статус "регистрация закрыта", тогда
    # нужно посмотреть, какие лимиты имеет этот ивент (у него может не быть какого-то
    # типа лимита, ведь эти поля необязательные) и какой формат был у отмененной заявки:
    # - если у ивента были оба лимита и заявка была офлайн, тогда меняем статус ивента
    # на "регистрация онлайн закрыта" (то есть возобновляем офлайн-регистрацию)
    # - если у ивента были оба лимита и заявка была онлайн, тогда меняем статус ивента
    # на "регистрация офлайн закрыта" (то есть возобновляем онлайн-регистрацию)
    # - DONE если у ивента был только офлайн-лимит и заявка была офлайн, то меняем
    # статус на "регистрация открыта"
    # - если у ивента был только онлайн-лимит и заявка была онлайн, то меняем статус
    # на "регистрация открыта"
    # - если у ивента был только офлайн-лимит, а заявка была онлайн, то не меняем статус
    # - если у ивента был только онлайн-лимит, а заявка была офлайн, то не меняем статус
    # - если у ивента не было лимитов, то у него и статус должен был все время
    # оставаться "регистрация открыта", но если админ в Админке вручную поменял статус
    # на "регистрация закрыта", а потом кто-то отменил заявку, то не меняем статус
    # ивента автоматически, пусть админ и дальше осуществляет ручное управление статусом
    # ивента, раз он уже начал вмешиваться в автоматическую смену статусов

    # ситуация 4: ивент имеет гибридный формат, офлайн-лимит и статус "регистрация
    # офлайн закрыта":
    # - DONE заявка была офлайн, тогда меняем статус ивента на "регистрация открыта"
    # - заявка была онлайн, тогда не меняем статус ивента

    # ситуация 5: ивент имеет гибридный формат, онлайн-лимит и статус "регистрация
    # онлайн закрыта":
    # - DONE заявка была онлайн, тогда меняем статус ивента на "регистрация открыта"
    # - заявка была офлайн, тогда не меняем статус ивента

    # TODO: add logging (event status changes)
    def perform_destroy(self, instance):
        """
        Deletes the application for participation in the event and re-opens
        registration for the event, if required.
        """
        event = instance.event
        application_format = instance.format
        instance.delete()
        logger.debug(
            f"The application of user {self.request.user} to participate "
            f"in event {event} was deleted."
        )

        if event.format != Event.FORMAT_HYBRID and event.status == Event.STATUS_CLOSED:
            event.status = Event.STATUS_OPEN
        if (
            event.format == Event.FORMAT_HYBRID
            and event.participant_offline_limit
            and event.status == Event.STATUS_OFFLINE_CLOSED
            and application_format == Event.FORMAT_OFFLINE
        ):
            event.status = Event.STATUS_OPEN
        if (
            event.format == Event.FORMAT_HYBRID
            and event.participant_online_limit
            and event.status == Event.STATUS_ONLINE_CLOSED
            and application_format == Event.FORMAT_ONLINE
        ):
            event.status = Event.STATUS_OPEN
        if (  # TODO: потестить руками
            event.format == Event.FORMAT_HYBRID
            and event.participant_offline_limit
            and not event.participant_online_limit
            and event.status == Event.STATUS_CLOSED
            and application_format == Event.FORMAT_OFFLINE
        ):
            event.status = Event.STATUS_OPEN
        event.save()


class NotificationSettingsViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """APIView to edit NotificationSettings by PATCH-requests."""

    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationSettingsSerializer
    http_method_names = ["get", "patch"]

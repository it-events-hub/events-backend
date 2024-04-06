from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet

from .models import Application
from .serializers import (
    ApplicationCreateAnonymousSerializer,
    ApplicationCreateAuthorizedSerializer,
)
from .utils_db_write import create_notification_settings
from api.loggers import logger
from api.permissions import IsAuthorOrCreateOnly
from events.models import Event
from users.models import Specialization


# TODO: Если заявка отменена авторизованным юзером, то открывать регистрацию снова.
# TODO: добавить в сериализаторы Event отображение количества поданных заявок
# (онлайн и офлайн)
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
            == event.participant_offline_limit
        )

    @staticmethod
    def check_online_event_limit(event: Event) -> bool:
        """Checks if the participant limit for the online event is reached."""
        return (
            event.format == Event.FORMAT_ONLINE
            and event.participant_online_limit
            and event.applications.filter(format=Event.FORMAT_ONLINE).count()
            == event.participant_online_limit
        )

    @staticmethod
    def check_hybrid_event_offline_limit(event: Event) -> bool:
        """Checks if the participant offline limit for the hybrid event is reached."""
        return (
            event.format == Event.FORMAT_HYBRID
            and event.participant_offline_limit
            and event.applications.filter(format=Event.FORMAT_OFFLINE).count()
            == event.participant_offline_limit
        )

    @staticmethod
    def check_hybrid_event_online_limit(event: Event) -> bool:
        """Checks if the participant online limit for the hybrid event is reached."""
        return (
            event.format == Event.FORMAT_HYBRID
            and event.participant_online_limit
            and event.applications.filter(format=Event.FORMAT_ONLINE).count()
            == event.participant_online_limit
        )

    @staticmethod
    def check_event_limits_and_close_registration(event: Event) -> None:
        """
        Checks event participant limits and closes registration if limits are reached.
        """
        if ApplicationViewSet.check_hybrid_event_offline_limit(event):
            event.status = Event.STATUS_OFFLINE_CLOSED
        elif ApplicationViewSet.check_hybrid_event_online_limit(event):
            event.status = Event.STATUS_ONLINE_CLOSED
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
        event.save()

    def perform_create(self, serializer):
        """
        Adds user to the application if request user is authenticated.
        Triggers notification settings instance creation if request user is anonymous.
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
        else:
            serializer.save()
            created_application_id = serializer.instance.id
            create_notification_settings(application_pk=created_application_id)
        ApplicationViewSet.check_event_limits_and_close_registration(
            serializer.validated_data["event"]
        )


# TODO: make endpoint to patch NotificationSettings

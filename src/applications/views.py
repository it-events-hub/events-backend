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

from .helpers import (
    EventClosureController,
    EventReopeningController,
    create_notification_settings,
)
from .models import Application, NotificationSettings
from .serializers import (
    ApplicationCreateAnonymousSerializer,
    ApplicationCreateAuthorizedSerializer,
    NotificationSettingsSerializer,
)
from api.loggers import logger
from api.permissions import IsAuthorOrCreateOnly
from users.models import Specialization


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

    def perform_create(self, serializer):
        """
        Adds the user to the application if the request user is authenticated.
        Triggers the authenticated user's data updating if the user changes this data
        in the application.
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
        EventClosureController.check_event_limits_and_close_registration(
            serializer.validated_data["event"]
        )

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
        EventReopeningController.check_event_limits_and_reopen_registration(
            event, application_format
        )


class NotificationSettingsViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """APIView to edit NotificationSettings by PATCH-requests."""

    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationSettingsSerializer
    http_method_names = ["get", "patch"]

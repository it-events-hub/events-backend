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
from users.models import Specialization


# TODO: при подаче заявок увеличивать лимиты у ивента, а если лимиты достигнуты,
# то закрывать регистрацию. Если заявка отменена авторизованным юзером, то отнять 1
# от лимита и открывать регистрацию снова.
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
        Adds user to the application if request user is authenticated.
        Triggers notification settings instance creation if request user is anonymous.
        """
        user: SimpleLazyObject | AnonymousUser = self.request.user
        if user.is_authenticated:
            self.__class__.update_authenticated_user_personal_data(
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

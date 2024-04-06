from typing import Any

from rest_framework.generics import CreateAPIView

from .models import Application
from .serializers import (
    ApplicationCreateAnonymousSerializer,
    ApplicationCreateAuthorizedSerializer,
)
from .utils_db_write import create_notification_settings
from users.models import Specialization


class ApplicationCreateAPIView(CreateAPIView):
    """APIView to create applications for participation in events."""

    queryset = Application.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return ApplicationCreateAuthorizedSerializer
        return ApplicationCreateAnonymousSerializer

    # TODO: сделать тут автозаполнение данных заявки
    def perform_create(self, serializer):
        """
        Adds user to the application if request user is authenticated.
        Triggers notification settings instance creation if request user is anonymous.
        """
        if self.request.user.is_authenticated:
            user_validated_data: list[Any] = {
                "first_name": serializer.validated_data.get("first_name"),
                "last_name": serializer.validated_data.get("last_name"),
                "email": serializer.validated_data.get("email"),
                "phone": serializer.validated_data.get("phone"),
                "telegram": serializer.validated_data.get("telegram"),
                "birth_date": serializer.validated_data.get("birth_date"),
                "city": serializer.validated_data.get("city"),
                "activity": serializer.validated_data.get("activity"),
                "company": serializer.validated_data.get("company"),
                "position": serializer.validated_data.get("position"),
                "experience_years": serializer.validated_data.get("experience_years"),
            }
            specializations: list[Specialization] = serializer.validated_data.get(
                "specializations"
            )
            if any(user_validated_data):
                for key, value in user_validated_data.items():
                    if value:
                        setattr(self.request.user, key, value)
            if specializations:
                self.request.user.specializations.set(specializations)
            self.request.user.save()
            serializer.save(user=self.request.user)
        else:
            serializer.save()
            created_application_id = serializer.instance.id
            create_notification_settings(application_pk=created_application_id)

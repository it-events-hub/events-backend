from rest_framework.generics import CreateAPIView

from .models import Application
from .serializers import (
    ApplicationCreateAnonymousSerializer,
    ApplicationCreateAuthorizedSerializer,
)
from .utils_db_write import create_notification_settings


class ApplicationCreateAPIView(CreateAPIView):
    """APIView to create applications for participation in events."""

    queryset = Application.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return ApplicationCreateAuthorizedSerializer
        return ApplicationCreateAnonymousSerializer

    # TODO: сделать тут сохранение новых данных пользователя? сейчас они через апи не
    # сохраняются, только через админку (там работает метод clean)
    # TODO: сделать тут автозаполнение данных заявки
    def perform_create(self, serializer):
        """
        Adds user to the application if request user is authenticated.
        Triggers notification settings instance creation if request user is anonymous.
        """
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
            created_application_id = serializer.instance.id
            create_notification_settings(application_pk=created_application_id)

from rest_framework.generics import CreateAPIView

from .models import Application
from .serializers import (
    ApplicationCreateAnonymousSerializer,
    ApplicationCreateAuthorizedSerializer,
)


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
        """Adds user to the application if the user is authenticated."""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        return super().perform_create(serializer)

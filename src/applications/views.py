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

    def perform_create(self, serializer):
        """Adds user to the application if the user is authenticated."""
        print(self.request.user)
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        return super().perform_create(serializer)

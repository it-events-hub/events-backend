from rest_framework.generics import CreateAPIView

from .models import Application
from .serializers import ApplicationCreateAnonymousSerializer


class ApplicationCreateAPIView(CreateAPIView):
    """APIView to create applications for participation in events."""

    queryset = Application.objects.all()
    serializer_class = ApplicationCreateAnonymousSerializer

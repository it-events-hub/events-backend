from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Event
from .serializers import EventDetailSerializer, EventSerializer


# TODO: добавить фильтрацию, разграничить доступ, добавить пагинацию
class EventViewSet(ModelViewSet):
    """
    ViewSet provides endpoints for listing, creating, retrieving, updating,
    partially updating, and deactivating events.
    """

    queryset = Event.objects.all()
    http_method_names = ["get", "post", "patch"]
    serializer_class = EventSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EventDetailSerializer
        return EventSerializer

    @action(
        detail=True,
        methods=["patch"],
    )
    def deactivate(self, request, pk=None):
        """Deactivate a specific event."""
        event = self.get_object()
        event.is_deleted = True
        event.save()
        return Response({"message": "Событие успешно деактивировано."})

    @action(
        detail=True,
        methods=["patch"],
    )
    def activate(self, request, pk=None):
        """Activate a specific event."""
        event = self.get_object()
        event.is_deleted = False
        event.save()
        return Response({"message": "Событие успешно активировано."})

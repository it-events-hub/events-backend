from django.utils import timezone
from django.utils.decorators import method_decorator
from django_filters import rest_framework as rf_filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from .models import Event
from .schemas import EVENT_LIST_DESCRIPTION, EVENT_LIST_FILTERS
from .serializers import (
    EventCreateSerializer,
    EventDeactivationSerializer,
    EventDetailSerializer,
    EventListSerializer,
)
from api.filters import EventsFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAdminOrReadOnly


# TODO: добавить permission_classes
@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_description=EVENT_LIST_DESCRIPTION,
        manual_parameters=EVENT_LIST_FILTERS,
    ),
)
class EventViewSet(ModelViewSet):
    """
    ViewSet provides endpoints for listing, creating, retrieving, updating,
    partially updating, and deactivating events.
    """

    queryset = Event.objects.prefetch_related("event_type", "parts", "specializations")
    http_method_names = ["get", "post", "patch"]
    filter_backends = [rf_filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = EventsFilter
    ordering_fields = ["start_time", "name"]
    ordering = ["pk"]
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return EventCreateSerializer
        if self.action == "retrieve":
            return EventDetailSerializer
        if self.action == "partial_update":
            return EventCreateSerializer
        if self.action == "activate" or self.action == "deactivate":
            return EventDeactivationSerializer
        return EventListSerializer

    def get_queryset(self):
        return EventListSerializer.setup_eager_loading(
            Event.objects.all(), user=self.request.user
        )

    @staticmethod
    def _change_event_status(request, instance, is_deleted):
        """Change the status of a spicific event."""
        data = {"is_deleted": is_deleted}
        serializer = EventDeactivationSerializer(instance, data=data)
        if serializer.is_valid():
            instance.is_deleted = is_deleted
            instance.save()
            serializer.save()
            response_serializer = EventDetailSerializer(instance)
            return Response(response_serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminUser])
    def deactivate(self, request, pk=None):
        """Deactivate a specific event."""
        instance = self.get_object()
        return self._change_event_status(request, instance, is_deleted=True)

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        """Activate a specific event."""
        instance = self.get_object()
        return self._change_event_status(request, instance, is_deleted=False)

    @action(
        detail=False,
        methods=["get"],
        url_path="three-recommended-events",
        permission_classes=[IsAuthenticated],
        filterset_class=None,
        pagination_class=None,
        ordering=None,
    )
    def three_recommended_events(self, request):
        """
        Shows three recommended events for authorized user according to
        the user's specializations.
        """
        now = timezone.now()
        specializations = request.user.specializations.all()
        all_future_events = (
            self.get_queryset().filter(start_time__gt=now).order_by("start_time")
        )
        recommended_future_events = list(
            all_future_events.filter(specializations__in=specializations)
        )
        if len(recommended_future_events) >= 3:
            result = recommended_future_events[:3]
        else:
            result = recommended_future_events
            additional_events_number: int = 3 - len(result)
            for event in all_future_events:
                if not additional_events_number:
                    break
                if event not in result:
                    result.append(event)
                    additional_events_number -= 1

        serializer = self.get_serializer_class()(
            result,
            many=True,
            context={"request": request, "format": self.format_kwarg, "view": self},
        )
        return Response(serializer.data, status=HTTP_200_OK)

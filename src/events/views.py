from django.utils.decorators import method_decorator
from django_filters import rest_framework as rf_filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Event
from .schemas import EVENT_LIST_DESCRIPTION, EVENT_LIST_FILTERS, EVENT_LIST_RESPONSES
from .serializers import EventCreateSerializer, EventSerializer
from api.filters import EventsFilter
from api.pagination import CustomPageNumberPagination


# TODO: добавить в сериализаторы Event отображение количества поданных заявок
# (онлайн и офлайн), в Админку тоже можно добавить
# TODO: добавить permission_classes
# TODO: сделать новый эндпойнт (@action) для показа авторизованному юзеру 3 персональных
# рекомнендаций, если у него в ЛК нет направлений, то 3 ближайших, если есть
# направления, то 3 ближайших с этими направлениями, если он будет показывать те же
# ивенты, что и основной эндпойнт Афиши, это не страшно
@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="list",
        operation_description=EVENT_LIST_DESCRIPTION,
        responses=EVENT_LIST_RESPONSES,
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
    serializer_class = EventSerializer
    filter_backends = [rf_filters.DjangoFilterBackend, OrderingFilter]  #
    filterset_class = EventsFilter
    ordering_fields = ["start_time", "name"]
    ordering = ["pk"]
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == "create":
            return EventCreateSerializer
        return EventSerializer

    def get_queryset(self):
        return EventSerializer.setup_eager_loading(
            Event.objects.all(), user=self.request.user
        )

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

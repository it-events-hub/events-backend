from django.db.models import BooleanField, ExpressionWrapper, Q
from django.utils import timezone
from django_filters import rest_framework as rf_filters

from events.models import Event


class CharFilterInFilter(rf_filters.BaseInFilter, rf_filters.CharFilter):
    """Custom char filter allowing comma-separated incoming values."""

    pass


class EventsFilter(rf_filters.FilterSet):
    """
    Class for filtering events.

    The filter for the 'name' field works on case-insensitive partial occurrence.
    The 'is_deleted' filter takes boolean values - True/False.
    The 'is_registrated' filter takes 0 as False and 1 as True.
    The 'not_started' filter takes True, False, 0 and 1 as value, otherwise
    returns all the events.
    The 'status' and 'format' filters accept one/several comma-separated string values.
    The 'event_type' filter accepts one/several comma-separated slug values.
    The 'specializations' filter accepts one/several comma-separated slug values.
    The 'city' filter accepts one/several comma-separated slug values.
    The 'start_date' and 'end_date' filters take datetime string
    (input examples: "2020-01-01", "2024-03-04T16:20:55") as input and compare it
    to the value of the 'start_time' field of each event.
    """

    name = rf_filters.CharFilter(method="istartswith_icontains_union_method")
    status = CharFilterInFilter()
    format = CharFilterInFilter()
    event_type = CharFilterInFilter(field_name="event_type__slug")
    specializations = CharFilterInFilter(field_name="specializations__slug")
    city = CharFilterInFilter(field_name="city__slug")
    start_date = rf_filters.DateTimeFilter(field_name="start_time", lookup_expr="gte")
    end_date = rf_filters.DateTimeFilter(field_name="start_time", lookup_expr="lte")
    is_registrated = rf_filters.NumberFilter(
        method="is_registrated_to_event_boolean_method"
    )
    not_started = rf_filters.BooleanFilter(method="event_not_started")

    class Meta:
        model = Event
        fields = [
            "name",
            "is_deleted",
            "is_registrated",
            "not_started",
            "status",
            "format",
            "event_type",
            "specializations",
            "city",
            "start_date",
            "end_date",
        ]

    def istartswith_icontains_union_method(self, queryset, name, value):
        """
        When using sqlite DB, filtering will be case-sensitive;
        when using PostgreSQL DB, filtering will be case-insensitive as it should be.
        """
        if not bool(value):
            return queryset
        return (
            queryset.filter(Q(name__istartswith=value) | Q(name__icontains=value))
            .annotate(
                is_start=ExpressionWrapper(
                    Q(name__istartswith=value),
                    output_field=BooleanField(),
                )
            )
            .order_by("-is_start")
        )

    def is_registrated_to_event_boolean_method(self, queryset, name, value):
        """
        Shows the authorized user whether this user has registered for the event.
        Always shows all the events to anonymous user.
        """
        if value not in [0, 1]:
            return queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset
        event_ids = [obj.pk for obj in queryset if obj.is_registrated == value]
        if event_ids:
            return queryset.filter(pk__in=event_ids)
        return queryset.none()

    def event_not_started(self, queryset, name, value):
        """
        Shows events that have not yet started.
        Takes True, False, 0 and 1 as value, otherwise returns all the events.
        """
        if value in [True, False]:
            now = timezone.now()
            if value:
                return queryset.filter(start_time__gt=now)
            return queryset.filter(start_time__lte=now)
        return queryset

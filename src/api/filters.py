from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters import rest_framework as rf_filters

from events.models import Event


class CharFilterInFilter(rf_filters.BaseInFilter, rf_filters.CharFilter):
    """Custom char filter allowing comma-separated incoming values."""

    pass


# TODO: прояснить ситуацию с фильтром по городу (place)
# TODO: сделать фильтр, началось ли событие (мы не должны базово показывать прошедшие
# события на странице Афиши, если на календаре не отмечен особый промежуток времени)
# TODO: сделать фильтр, показывающий авторизованному, регался ли он на ивент (по типу
# фильтра is_favorited)
class EventsFilter(rf_filters.FilterSet):
    """
    Class for filtering events.

    The filter for the 'name' field works on case-insensitive partial occurrence.
    The 'is_deleted' filter takes boolean values - True/False.
    The 'status' and 'format' filters accept one/several comma-separated string values.
    The 'event_type' filter accepts one/several comma-separated slug values.
    The 'specializations' filter accepts one/several comma-separated slug values.
    The 'start_date' and 'end_date' filters take datetime string
    (input examples: "2020-01-01", "2024-03-04T16:20:55") as input and compare it
    to the value of the 'start_time' field of each event.
    """

    name = rf_filters.CharFilter(method="istartswith_icontains_union_method")
    status = CharFilterInFilter()
    format = CharFilterInFilter()
    event_type = CharFilterInFilter(field_name="event_type__slug")
    specializations = CharFilterInFilter(field_name="specializations__slug")
    start_date = rf_filters.DateTimeFilter(field_name="start_time", lookup_expr="gte")
    end_date = rf_filters.DateTimeFilter(field_name="start_time", lookup_expr="lte")

    class Meta:
        model = Event
        fields = [
            "name",
            "is_deleted",
            "status",
            "format",
            "event_type",
            "specializations",
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

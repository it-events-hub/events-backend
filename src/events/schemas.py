from drf_yasg import openapi

from .models import Event
from .serializers import EventSerializer

EVENT_LIST_DESCRIPTION: str = (
    "Endpoint to get list of events, accessible to both authorized and unauthorized "
    "visitors, events can be filtered and sorted (ordered)."
)
EVENT_LIST_RESPONSES = {200: EventSerializer}
EVENT_LIST_FILTERS = [
    openapi.Parameter(
        "name",
        openapi.IN_QUERY,
        description=(
            "filtering by partial occurrence at the beginning or other parts "
            "of the name"
        ),
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "is_deleted",
        openapi.IN_QUERY,
        description=(
            "filtering by is_deleted field, showing whether the event is deactivated"
        ),
        type=openapi.TYPE_BOOLEAN,
    ),
    openapi.Parameter(
        "status",
        openapi.IN_QUERY,
        description=(
            "filtering by event statuses, filter accepts one or several "
            "comma-separated values, input examples: "
            "?status=registration%20is%20open%2Cregistration%20is%20closed, "
            "?status=registration%20is%20closed"
        ),
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(
            enum=[
                Event.STATUS_OPEN,
                Event.STATUS_OFFLINE_CLOSED,
                Event.STATUS_ONLINE_CLOSED,
                Event.STATUS_CLOSED,
            ],
            type=openapi.TYPE_STRING,
        ),
    ),
    openapi.Parameter(
        "format",
        openapi.IN_QUERY,
        description=(
            "filtering by event formats, filter accepts one or several comma-separated "
            "values, input examples: ?format=offline,hybrid, ?format=online"
        ),
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(
            enum=[
                Event.FORMAT_OFFLINE,
                Event.FORMAT_ONLINE,
                Event.FORMAT_HYBRID,
            ],
            type=openapi.TYPE_STRING,
        ),
    ),
    openapi.Parameter(
        "event_type",
        openapi.IN_QUERY,
        description=(
            "filtering by event types, filter accepts one or several comma-separated "
            "slug values, input example: ?event_type=conference%2Cmeetup"
        ),
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_SLUG,
    ),
    openapi.Parameter(
        "specializations",
        openapi.IN_QUERY,
        description=(
            "filtering by event specializations, filter accepts one or several "
            "comma-separated slug values, input example: "
            "?specializations=backend,analytics"
        ),
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_SLUG,
    ),
    openapi.Parameter(
        "start_date",
        openapi.IN_QUERY,
        description=(
            "filtering by earliest event start time including input value, "
            "input examples: '2020-01-01', '2024-03-04T16:20:55'"
        ),
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATETIME,
    ),
    openapi.Parameter(
        "end_date",
        openapi.IN_QUERY,
        description=(
            "filtering by latest event start time including input value, "
            "input examples: '2020-01-01', '2024-03-04T16:20:55'"
        ),
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATETIME,
    ),
]

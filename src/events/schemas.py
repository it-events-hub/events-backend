from drf_yasg import openapi

from .models import Event

EVENT_LIST_DESCRIPTION: str = (
    "Endpoint to get list of events, accessible to both authorized and unauthorized "
    "visitors, events can be filtered and sorted (ordered)."
)
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
        "is_registrated",
        openapi.IN_QUERY,
        description=(
            "Shows the authorized user whether this user has registered for the event. "
            "Always shows all the events to anonymous user. Takes 0 as False and "
            "1 as True. Input examples: ?is_registrated=0, ?is_registrated=1"
        ),
        type=openapi.TYPE_INTEGER,
    ),
    openapi.Parameter(
        "not_started",
        openapi.IN_QUERY,
        description=(
            "Shows events that have not yet started. Takes True, False, 0 and 1 "
            "as input values, otherwise returns all the events. Input example: "
            "?not_started=True"
        ),
        type=openapi.TYPE_BOOLEAN,
    ),
    openapi.Parameter(
        "is_featured",
        openapi.IN_QUERY,
        description=(
            "Shows events that we promote on the Main page. Takes True, False, 0 and 1 "
            "as input values, otherwise returns all the events. Input examples: "
            "?is_featured=True, ?is_featured=0 (0 means False)"
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
        "city",
        openapi.IN_QUERY,
        description=(
            "filtering by event cities, filter accepts one or several "
            "comma-separated slug values, input example: ?city=moscow,kazan"
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
    openapi.Parameter(
        "ordering",
        openapi.IN_QUERY,
        description=(
            "Which field to use when ordering the results. You can sort objects by "
            "id (default), start_time (start_time chronological order) and name "
            "(alphabetical order). Input examples: ?ordering=start_time, ?ordering=name"
        ),
        type=openapi.TYPE_STRING,
    ),
]

from rest_framework.serializers import ModelSerializer

from .models import Event, EventPart, EventType
from users.models import Specialization


class EventTypeSerializer(ModelSerializer):
    """Serializer for handling event types."""

    class Meta:
        model = EventType
        fields = "__all__"


class SpecializationSerializer(ModelSerializer):
    """Serializer for handling specialization types."""

    class Meta:
        model = Specialization
        fields = "__all__"


class EventPartSerializer(ModelSerializer):
    """Serializer for handling event parts."""

    class Meta:
        model = EventPart
        fields = "__all__"


class EventSerializer(ModelSerializer):
    """Serializer for handling a list of events."""

    event_type = EventTypeSerializer()
    specializations = SpecializationSerializer()

    class Meta:
        model = Event
        fields = "__all__"


class EventDetailSerializer(EventSerializer):
    """Serializer for displaying detailed information about an event."""

    event_parts = EventPartSerializer(many=True, source="parts")

    class Meta(EventSerializer.Meta):
        pass

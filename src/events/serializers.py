from rest_framework.serializers import ModelSerializer

from .models import Event, EventPart, EventType, Speaker
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
        ref_name = "SpecializationUsers"


class SpeakerSerializer(ModelSerializer):
    """Serializer for handling speakers."""

    class Meta:
        model = Speaker
        fields = "__all__"


class EventPartSerializer(ModelSerializer):
    """Serializer for handling event parts."""

    speaker = SpeakerSerializer()

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

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Performs necessary eager loading of events."""
        return queryset.select_related("event_type", "specializations")

    def create(self, validated_data):
        event_type_id = validated_data.pop("event_type_id", None)
        event_type_data = validated_data.pop("event_type", None)
        specializations_data = validated_data.pop("specializations", None)

        event = Event.objects.create(**validated_data)

        if event_type_id:
            event_type, created = EventType.objects.get_or_create(id=event_type_id)
            event.event_type = event_type

        elif event_type_data:
            event_type_serializer = EventTypeSerializer(data=event_type_data)
            if event_type_serializer.is_valid():
                event_type = event_type_serializer.save()
                event.event_type = event_type

        specializations_serializer = SpecializationSerializer(data=specializations_data)
        if specializations_serializer.is_valid():
            specializations = specializations_serializer.save()
            event.specializations = specializations

        event.save()
        return event

    def update(self, instance, validated_data):
        # for attr, value in validated_data.items():
        #     setattr(instance, attr, value)
        instance.name = validated_data.get("name", instance.name)
        instance.organization = validated_data.get(
            "organization", instance.organization
        )

        event_type_data = validated_data.pop("event_type")
        event_type_serializer = EventTypeSerializer(
            instance.event_type, data=event_type_data
        )

        if event_type_serializer.is_valid():
            event_type_serializer.save()

        instance.save()
        return instance


class EventDetailSerializer(EventSerializer):
    """Serializer for displaying detailed information about an event."""

    event_parts = EventPartSerializer(many=True, source="parts")

    class Meta(EventSerializer.Meta):
        pass

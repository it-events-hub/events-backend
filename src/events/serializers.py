from rest_framework import serializers

from .models import Event, EventPart, EventType, Speaker
from users.models import Specialization


class EventTypeSerializer(serializers.ModelSerializer):
    """Serializer for handling event types."""

    class Meta:
        model = EventType
        fields = "__all__"


class SpecializationSerializer(serializers.ModelSerializer):
    """Serializer for handling specialization types."""

    class Meta:
        model = Specialization
        fields = "__all__"
        ref_name = "UserSpecialization"


class SpeakerSerializer(serializers.ModelSerializer):
    """Serializer for handling speakers."""

    class Meta:
        model = Speaker
        fields = "__all__"


class EventPartSerializer(serializers.ModelSerializer):
    """Serializer for handling event parts."""

    speaker = SpeakerSerializer(read_only=True)

    class Meta:
        model = EventPart
        fields = "__all__"


# TODO: сделать валидацию (метод validate в сериализаторе создания/редактирования нового
# ивента), что если формат ивента офлайн или гибрид, то поле place обязательно для
# заполнения
class EventSerializer(serializers.ModelSerializer):
    """Serializer for handling a list of events."""

    event_type = EventTypeSerializer(read_only=True)
    specializations = SpecializationSerializer(read_only=True)
    event_parts = EventPartSerializer(many=True, source="parts")

    class Meta:
        model = Event
        fields = "__all__"

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Performs necessary eager loading of events."""
        return queryset.select_related("event_type", "specializations")


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an event."""

    class Meta:
        model = Event
        fields = [
            "name",
            "description",
            "specializations",
            "start_time",
            "format",
            "place",
            "participant_offline_limit",
            "participant_online_limit",
            "livestream_link",
            "additional_materials_link",
            "is_featured",
            "is_featured_on_yandex_afisha",
            "event_type",
        ]

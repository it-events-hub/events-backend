from django.db.models import Prefetch
from rest_framework import serializers

from .models import Event, EventPart, EventType, Speaker
from users.models import Specialization


class EventTypeSerializer(serializers.ModelSerializer):
    """Serializer for handling event types."""

    event_type_name = serializers.CharField(
        source="name",
        label=EventType._meta.get_field("name").verbose_name,
        max_length=EventType._meta.get_field("name").max_length,
    )
    event_type_slug = serializers.SlugField(
        source="slug",
        label=EventType._meta.get_field("slug").verbose_name,
        max_length=EventType._meta.get_field("slug").max_length,
    )

    class Meta:
        model = EventType
        fields = ["id", "event_type_name", "event_type_slug"]


class SpecializationSerializer(serializers.ModelSerializer):
    """Serializer for handling specialization types."""

    specialization_name = serializers.CharField(
        source="name",
        label=Specialization._meta.get_field("name").verbose_name,
        max_length=Specialization._meta.get_field("name").max_length,
    )
    specialization_slug = serializers.SlugField(
        source="slug",
        label=Specialization._meta.get_field("slug").verbose_name,
        max_length=Specialization._meta.get_field("slug").max_length,
    )

    class Meta:
        model = Specialization
        fields = ["id", "specialization_name", "specialization_slug"]
        ref_name = "UserSpecialization"


class SpeakerSerializer(serializers.ModelSerializer):
    """Serializer for handling speakers."""

    speaker_name = serializers.CharField(
        source="name",
        label=Speaker._meta.get_field("name").verbose_name,
        max_length=Speaker._meta.get_field("name").max_length,
    )
    speaker_description = serializers.CharField(
        source="description",
        label=Speaker._meta.get_field("description").verbose_name,
    )

    class Meta:
        model = Speaker
        fields = [
            "id",
            "speaker_name",
            "company",
            "position",
            "speaker_description",
            "photo",
        ]


class EventPartSerializer(serializers.ModelSerializer):
    """Serializer for handling event parts."""

    speaker = SpeakerSerializer(read_only=True, allow_null=True)
    event_part_is_deleted = serializers.BooleanField(
        source="is_deleted",
        label=EventPart._meta.get_field("is_deleted").verbose_name,
    )
    event_part_name = serializers.CharField(
        source="name",
        label=EventPart._meta.get_field("name").verbose_name,
        max_length=EventPart._meta.get_field("name").max_length,
    )
    event_part_description = serializers.CharField(
        source="description",
        label=EventPart._meta.get_field("description").verbose_name,
        allow_null=True,
    )
    event_part_created = serializers.DateTimeField(
        source="created",
        label=EventPart._meta.get_field("created").verbose_name,
    )
    event_part_start_time = serializers.DateTimeField(
        source="start_time",
        label=EventPart._meta.get_field("start_time").verbose_name,
    )

    class Meta:
        model = EventPart
        fields = [
            "id",
            "speaker",
            "event_part_is_deleted",
            "event_part_name",
            "event_part_description",
            "event_part_created",
            "event_part_start_time",
            "presentation_type",
            "event",
        ]


# TODO: сделать валидацию (метод validate в сериализаторе создания/редактирования нового
# ивента), что если формат ивента офлайн или гибрид, то поле place обязательно для
# заполнения
class EventSerializer(serializers.ModelSerializer):
    """Serializer for handling a list of events."""

    event_type = EventTypeSerializer(read_only=True)
    specializations = SpecializationSerializer(read_only=True)
    event_parts = EventPartSerializer(many=True, source="parts")

    # поменяла порядок полей, чтобы название ивента было выше, а вложенные объекты ниже
    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "is_deleted",
            "organization",
            "description",
            "status",
            "format",
            "created",
            "start_time",
            "end_time",
            "cost",
            "place",
            "participant_offline_limit",
            "participant_online_limit",
            "registration_deadline",
            "livestream_link",
            "additional_materials_link",
            "image",
            "is_featured",
            "is_featured_on_yandex_afisha",
            "event_type",
            "specializations",
            "event_parts",
        ]

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Performs necessary eager loading of events."""
        return queryset.select_related(
            "event_type", "specializations"
        ).prefetch_related(
            Prefetch("parts", queryset=EventPart.objects.select_related("speaker"))
        )


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

from django.db.models import Exists, OuterRef, Prefetch
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from .models import City, Event, EventPart, EventType, Speaker
from applications.models import Application
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


class CitySerializer(serializers.ModelSerializer):
    """Serializer for handling cities of events."""

    city_name = serializers.CharField(
        source="name",
        label=City._meta.get_field("name").verbose_name,
        max_length=City._meta.get_field("name").max_length,
    )
    city_slug = serializers.SlugField(
        source="slug",
        label=City._meta.get_field("slug").verbose_name,
        max_length=City._meta.get_field("slug").max_length,
    )

    class Meta:
        model = City
        fields = ["id", "city_name", "city_slug"]


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
            "event_part_name",
            "event_part_description",
            "event_part_created",
            "event_part_start_time",
            "presentation_type",
            "event",
        ]


class EventListSerializer(serializers.ModelSerializer):
    """Serializer for handling a list of events."""

    event_type = EventTypeSerializer(read_only=True)
    city = CitySerializer(allow_null=True)
    specializations = SpecializationSerializer(read_only=True)
    is_registrated = serializers.SerializerMethodField()
    submitted_applications = serializers.SerializerMethodField()
    first_speaker = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "is_deleted",
            "is_registrated",
            "submitted_applications",
            "first_speaker",
            "organization",
            "description",
            "status",
            "format",
            "created",
            "start_time",
            "end_time",
            "cost",
            "city",
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
        ]

    @classmethod
    def setup_eager_loading(cls, queryset, user):
        """Performs necessary eager loading of events."""
        if user.is_anonymous:
            return queryset.select_related(
                "event_type", "specializations", "city"
            ).prefetch_related(
                "applications",
                Prefetch("parts", queryset=EventPart.objects.select_related("speaker")),
            )
        return (
            queryset.select_related("event_type", "specializations", "city")
            .prefetch_related(
                "applications",
                Prefetch("parts", queryset=EventPart.objects.select_related("speaker")),
            )
            .annotate(
                is_registrated=Exists(
                    Application.objects.filter(user=user, event=OuterRef("id"))
                )
            )
        )

    def get_is_registrated(self, obj) -> bool:
        """Shows the authorized user whether this user has registered for the event."""
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.is_registrated

    def get_submitted_applications(self, obj) -> int:
        """Shows the number of applications submitted to participate in the event."""
        return obj.applications.count()

    @swagger_serializer_method(SpeakerSerializer)
    def get_first_speaker(self, obj):
        """Shows the speaker of the first presentation of the event."""
        if obj.parts:
            speakers = [part.speaker for part in obj.parts.all() if part.speaker]
            if speakers:
                return SpeakerSerializer(speakers[0]).data
        return None


class EventDetailSerializer(EventListSerializer):
    """Serializer to retrieve one event."""

    event_parts = EventPartSerializer(many=True, source="parts")

    class Meta(EventListSerializer.Meta):
        fields = [
            "id",
            "name",
            "is_deleted",
            "is_registrated",
            "organization",
            "description",
            "status",
            "format",
            "created",
            "start_time",
            "end_time",
            "cost",
            "city",
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


# TODO: сделать валидацию (метод validate в сериализаторе создания/редактирования нового
# ивента), что если формат ивента офлайн или гибрид, то поля city и place должны быть
# заполнены
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
            "city",
        ]


class EventDeactivationSerializer(serializers.ModelSerializer):
    """Serializer for event deactivation."""

    class Meta:
        model = Event
        fields = ["id", "is_deleted"]

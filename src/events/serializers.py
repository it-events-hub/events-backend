from django.db import transaction
from django.db.models import Exists, OuterRef, Prefetch
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from .models import City, Event, EventPart, EventType, Speaker
from .utils import EVENT_CITY_REQUIRED_ERROR, EVENT_PLACE_REQUIRED_ERROR
from api.services.image_decoder import Base64ImageField
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

    # id = serializers.IntegerField(required=False)
    speaker_name = serializers.CharField(
        source="name",
        label=Speaker._meta.get_field("name").verbose_name,
        max_length=Speaker._meta.get_field("name").max_length,
    )
    speaker_description = serializers.CharField(
        source="description",
        label=Speaker._meta.get_field("description").verbose_name,
        required=False,
    )
    photo = Base64ImageField(required=False, allow_null=True)

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

    # id = serializers.IntegerField(required=False)
    speaker = SpeakerSerializer(allow_null=True)
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
        ]


class EventListSerializer(serializers.ModelSerializer):
    """Serializer for handling a list of events."""

    event_type = EventTypeSerializer(read_only=True)
    city = CitySerializer(allow_null=True)
    specializations = SpecializationSerializer(read_only=True)
    is_registrated = serializers.SerializerMethodField()
    submitted_applications = serializers.SerializerMethodField()
    first_speaker = serializers.SerializerMethodField()
    image = Base64ImageField()

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
        """Performs necessary joins and annotations for eager loading of event list."""
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
        """
        Shows for the authorized user whether this user has registered for the event.
        """
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
    image = Base64ImageField()

    class Meta(EventListSerializer.Meta):
        fields = [
            "id",
            "name",
            "is_deleted",
            "is_registrated",
            "submitted_applications",
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


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an event."""

    image = Base64ImageField(required=False)
    format = serializers.ChoiceField(
        choices=Event.FORMAT_CHOISES, label=Event._meta.get_field("format").verbose_name
    )
    event_parts = EventPartSerializer(many=True, source="parts")

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "event_type",
            "specializations",
            "format",
            "start_time",
            "end_time",
            "city",
            "place",
            "participant_offline_limit",
            "participant_online_limit",
            "registration_deadline",
            "status",
            "livestream_link",
            "additional_materials_link",
            "is_featured",
            "is_featured_on_yandex_afisha",
            "image",
            "cost",
            "event_parts",
        ]

    @transaction.atomic
    def create(self, validated_data):
        event_parts = validated_data.pop("parts")
        event = Event.objects.create(**validated_data)
        for part in event_parts:
            speaker_data = part.pop("speaker")
            speaker, _ = Speaker.objects.get_or_create(**speaker_data)
            EventPart.objects.create(event=event, speaker=speaker, **part)
        return event

    @transaction.atomic
    def update(self, instance, validated_data):
        event_parts = validated_data.pop("parts")

        for attrs, value in validated_data.items():
            setattr(instance, attrs, value)
        instance.save()

        # TODO: по умолчанию Django не поддерживает вложенные сериализаторы,
        # поэтому они доступны только для чтения.
        # Надо подумать как это решить...

        # part_ids_to_keep = [part_data.get("id") for part_data in event_parts if part_data.get("id")]

        # # Удаляем части мероприятия, которые не указаны в новых данных
        # instance.parts.exclude(id__in=part_ids_to_keep).delete()

        # for part in event_parts:
        #     part_id = part.get("id")
        #     if part_id:
        #         event_part = EventPart.objects.get(id=part_id, event=instance)
        #         speaker_data = part.get("speaker")
        #         speaker_id = speaker_data.get("id")
        #         if speaker_id:
        #             speaker, _ = Speaker.objects.get_or_create(id=speaker_id)
        #             for key, value in speaker_data.items():
        #                 setattr(speaker, key, value)
        #             speaker.save()
        #         event_part.save()
        #     else:
        #         speaker_data = part.pop("speaker")
        #         speaker_id = speaker_data.get("id")
        #         if speaker_id:
        #             speaker, _ = Speaker.objects.get_or_create(id=speaker_id)
        #             for key, value in speaker_data.items():
        #                 setattr(speaker, key, value)
        #             speaker.save()
        #         else:
        #             speaker = Speaker.objects.create(**speaker_data)
        #         EventPart.objects.create(event=instance, speaker=speaker, **part)
        return instance

    def validate(self, attrs):
        """
        Validates the data for creating or updating an event.
        City and place fields are required for offline or hybrid events.
        """
        format = attrs.get("format")
        city = attrs.get("city")
        place = attrs.get("place")
        if format in [Event.FORMAT_OFFLINE, Event.FORMAT_HYBRID]:
            if not city:
                raise serializers.ValidationError(EVENT_CITY_REQUIRED_ERROR)
            if not place:
                raise serializers.ValidationError(EVENT_PLACE_REQUIRED_ERROR)
        return attrs


class EventDeactivationSerializer(serializers.ModelSerializer):
    """Serializer for event deactivation."""

    class Meta:
        model = Event
        fields = ["id"]

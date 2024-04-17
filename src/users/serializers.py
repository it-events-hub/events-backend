from django.db import transaction
from rest_framework import serializers

from .models import Specialization, User
from .utils import check_birth_date
from applications.serializers import NotificationSettingsSerializer


class SpecializationSerializer(serializers.ModelSerializer):
    """Serializer to display specializations."""

    slug = serializers.SlugField()

    class Meta:
        model = Specialization
        fields = ("name", "slug")


class UserSerializer(serializers.ModelSerializer):
    """Serializer to display data in the user's personal account."""

    specializations = SpecializationSerializer(many=True)
    notification_settings = NotificationSettingsSerializer()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "telegram",
            "birth_date",
            "city",
            "activity",
            "company",
            "position",
            "experience_years",
            "specializations",
            "notification_settings",
            "is_staff",
        )


class UserUpdateSerializer(UserSerializer):
    """Serializer to update data in the user's personal account."""

    specializations = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(), many=True, required=False
    )

    class Meta(UserSerializer.Meta):
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "telegram",
            "birth_date",
            "city",
            "activity",
            "company",
            "position",
            "experience_years",
            "specializations",
        )

    def validate_birth_date(self, value):
        """Checks the user's birth date."""
        birth_date_error: str | None = check_birth_date(value)
        if birth_date_error:
            raise serializers.ValidationError(birth_date_error)

    @transaction.atomic
    def update(self, instance: User, validated_data: dict) -> User:
        """
        Creates m2m connections between the user and specializations during
        PATCH-requests to edit this user.
        """
        if validated_data.get("specializations") is not None:
            specializations: dict = validated_data.pop("specializations")
            instance.specializations.clear()
            instance.specializations.set(specializations)
        for field in validated_data:
            setattr(instance, field, validated_data[field])
        instance.save()
        return instance

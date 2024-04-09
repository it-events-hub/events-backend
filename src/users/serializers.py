from rest_framework import serializers

from .models import Specialization, User

# class PasswordSerializer(serializers.ModelSerializer):
#     new_password = serializers.CharField(required=True)
#     old_password = serializers.CharField(required=True)
#
#     class Meta:
#         model = User
#         fields = (
#             "new_password",
#             "old_password",
#         )


class SpecializationSerializer(serializers.ModelSerializer):
    """Serializer to display specializations."""

    slug = serializers.SlugField()

    class Meta:
        model = Specialization
        fields = ("name", "slug")


class UserSerializer(serializers.ModelSerializer):
    """Serializer to display data in the user's personal account."""

    specializations = SpecializationSerializer(many=True)

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
        )
        read_only_fields = ("id", "email")


class UserUpdateSerializer(UserSerializer):
    """Serializer to update data in the user's personal account."""

    specializations = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(), many=True
    )

    class Meta(UserSerializer.Meta):
        pass

    def update(self, instance: User, validated_data: dict) -> User:
        for item in validated_data.items():
            if item[0] in [
                "specializations",
                "id",
                "email",
            ]:
                continue
            instance.__dict__[item[0]] = item[1]
        instance.save()

        if "specializations" in validated_data:
            specializations: dict = validated_data.pop("specializations")
            instance.specializations.clear()
            instance.specializations.set(specializations)

        return instance

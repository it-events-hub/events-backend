from http import HTTPStatus

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
    slug = serializers.SlugField()

    class Meta:
        model = Specialization
        fields = ("name", "slug")


class UserSerializer(serializers.ModelSerializer):
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

    def update(self, instance: User, validated_data: dict) -> User:
        breakpoint()
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
            breakpoint()
            specializations: dict = validated_data.pop("specializations")
            User.specializations.through.filter(user=instance).delete()
            specs = [
                User.specializations.through(
                    user=instance,
                    specialization=spec,
                )
                for spec in specializations
            ]
            User.specializations.through.bulk_create(specs)

        return instance

    def validate_specializations(self, value: list) -> list:
        if not value:
            raise serializers.ValidationError(
                'Поле "Направление" обязательно к заполнению',
                code=HTTPStatus.BAD_REQUEST,
            )

        spec_ids = {s.id for s in value}
        if len(spec_ids) != len(value):
            raise serializers.ValidationError(
                "Повтор направления",
                code=HTTPStatus.BAD_REQUEST,
            )

        return value

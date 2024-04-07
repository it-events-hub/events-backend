from rest_framework import serializers

from .models import Specialization, User


class PasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "new_password",
            "old_password",
        )


class SpecializationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specialization
        fields = "__all__"


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
        # instance.first_name = validated_data.get(
        #     'first_name',
        #     instance.first_name,
        # )
        # instance.last_name = validated_data.get(
        #     'last_name',
        #     instance.last_name,
        # )
        # instance.phone = validated_data.get(
        #     'phone',
        #     instance.phone,
        # )
        # instance.telegram = validated_data.get(
        #     'telegram',
        #     instance.telegram,
        # )
        # instance.birth_date = validated_data.get(
        #     'birth_date',
        #     instance.birth_date,
        # )
        # TODO: Massively test/debug this
        for field in instance._meta.get_fields():
            if field.name in [
                "specializations",
                "id",
                "email",
            ]:
                continue
            instance.field = validated_data.get(
                field.name,
                field.value,
            )

        specializations: dict = validated_data.pop("specializations")
        User.specializations.through.filter(user=instance).delete()  # TODO: wtf?!
        specs = [
            User.specializations.through(
                user=instance,
                specialization=spec,
            )
            for spec in specializations
        ]
        User.specializations.through.bulk_create(specs)

        return instance

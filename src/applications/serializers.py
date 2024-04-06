from typing import Any

from django.utils.functional import SimpleLazyObject
from rest_framework import serializers

from .models import Application, NotificationSettings
from .utils import (
    APPLICATION_EVENT_EMAIL_UNIQUE_ERROR,
    APPLICATION_EVENT_PHONE_UNIQUE_ERROR,
    APPLICATION_EVENT_TELEGRAM_UNIQUE_ERROR,
    check_another_user_email,
    check_another_user_phone,
    check_another_user_telegram,
)
from events.models import Event
from users.models import Specialization, User
from users.utils import check_birth_date

APPLICATION_ACTIVITY_ANONYMOUS_ERROR: str = "Укажите компанию, должность и опыт."
APPLICATION_ACTIVITY_AUTHORIZED_ERROR: str = (
    "Укажите компанию, должность и опыт в заявке или в своем Личном кабинете перед "
    "подачей заявки."
)
APPLICATION_FORMAT_REQUIRED_ERROR: str = (
    "Если мероприятие имеет гибридный формат, в заявке обязательно должен быть указан "
    "желаемый формат участия."
)
APPLICATION_SPECIALIZATIONS_REQUIRED_ERROR: str = (
    "Укажите направления в заявке или в своем Личном кабинете перед подачей заявки."
)


# TODO: у ивента есть participant_offline_limit и participant_online_limit, если
# достигнут один из этих лимитов (и ивент гибридного формата), как нам закрывать
# регистрацию для одного формата, но оставить ее для второго формата, лимит по которому
# не достигнут?
# Как вариант, добавить ивентам еще два статуса (регистрация онлайн закрыта, регистрация
# офлайн закрыта).
# Еще вариант: при создании заявки (если регистрация еще открыта) проверять оба лимита,
# если по нужному нам формату участия лимит достигнут, то не создавать заявку и кидать
# ошибку (например, 'Офлайн места закончились, зарегистрируйтесь онлайн', и наоборот),
# а если при проверке выяснится, что оба лимита достигнуты, то автоматически менять
# статус ивента на 'регистрация закрыта'
class ApplicationCreateAuthorizedSerializer(serializers.ModelSerializer):
    """Serializer to create applications on behalf of authorized site visitors."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    activity = serializers.ChoiceField(
        choices=User.ACTIVITY_CHOISES,
        label=Application._meta.get_field("activity").verbose_name,
        required=False,
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "user",
            "event",
            "format",
            "source",
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
        ]

    def validate_birth_date(self, value):
        """Validates birth date."""
        birth_date_error: str | None = check_birth_date(value)
        if birth_date_error:
            raise serializers.ValidationError(birth_date_error)
        return value

    @staticmethod
    def check_format(attrs: dict[str, Any]) -> str | None:
        """Checks that attrs include a format field if the event has a hybrid format."""
        if attrs["event"].format == Event.FORMAT_HYBRID and not attrs.get("format"):
            return APPLICATION_FORMAT_REQUIRED_ERROR
        return None

    @staticmethod
    def check_email(attrs: dict[str, Any], user: SimpleLazyObject | None) -> str | None:
        """
        Checks that the email does not belong to another user and that
        there is no application for the same event with the same email.
        """
        another_user_email_error: str | None = check_another_user_email(
            user=user, email=attrs.get("email")
        )
        if another_user_email_error:
            return another_user_email_error
        same_email_in_attrs: bool = bool(
            attrs.get("email") is not None
            and Application.objects.filter(
                event=attrs["event"], email=attrs.get("email")
            ).exists()
        )
        same_email_in_user_personal_data: bool = bool(
            attrs.get("email") is None
            and Application.objects.filter(
                event=attrs["event"], email=user.email
            ).exists()
        )
        if same_email_in_attrs or same_email_in_user_personal_data:
            return APPLICATION_EVENT_EMAIL_UNIQUE_ERROR
        return None

    @staticmethod
    def check_phone(attrs: dict[str, Any], user: SimpleLazyObject | None) -> str | None:
        """
        Checks that the phone does not belong to another user and that
        there is no application for the same event with the same phone.
        """
        another_user_phone_error: str | None = check_another_user_phone(
            user=user, phone=attrs.get("phone")
        )
        if another_user_phone_error:
            return another_user_phone_error
        same_phone_in_attrs: bool = bool(
            attrs.get("phone") is not None
            and Application.objects.filter(
                event=attrs["event"], phone=attrs.get("phone")
            ).exists()
        )
        same_phone_in_user_personal_data: bool = bool(
            attrs.get("phone") is None
            and Application.objects.filter(
                event=attrs["event"], phone=user.phone
            ).exists()
        )
        if same_phone_in_attrs or same_phone_in_user_personal_data:
            return APPLICATION_EVENT_PHONE_UNIQUE_ERROR
        return None

    @staticmethod
    def check_telegram(
        attrs: dict[str, Any], user: SimpleLazyObject | None
    ) -> str | None:
        """
        Checks that the telegram does not belong to another user and that
        there is no application for the same event with the same telegram.
        """
        another_user_telegram_error: str | None = check_another_user_telegram(
            user=user, telegram=attrs.get("telegram")
        )
        if another_user_telegram_error:
            return another_user_telegram_error
        same_telegram_in_attrs: bool = bool(
            attrs.get("telegram") is not None
            and Application.objects.filter(
                event=attrs["event"], phone=attrs.get("telegram")
            ).exists()
        )
        same_telegram_in_user_personal_data: bool = bool(
            user
            and attrs.get("telegram") is None
            and Application.objects.filter(
                event=attrs["event"], telegram=user.telegram
            ).exists()
        )
        if same_telegram_in_attrs or same_telegram_in_user_personal_data:
            return APPLICATION_EVENT_TELEGRAM_UNIQUE_ERROR
        return None

    @staticmethod
    def check_activity(
        attrs: dict[str, Any], user: SimpleLazyObject | None
    ) -> str | None:
        """
        Checks if activity is set to 'working', then there should be data for
        company, position, and experience_years.
        """
        work, study, seek = User.ACTIVITY_WORK, User.ACTIVITY_STUDY, User.ACTIVITY_SEEK
        anonymous_working: bool = not user and attrs["activity"] == work
        anonymous_no_work_details: bool = not (
            attrs.get("company")
            and attrs.get("position")
            and attrs.get("experience_years")
        )
        authorized_working: bool = user and (
            (user.activity == work and attrs.get("activity") not in [study, seek])
            or (user.activity != work and attrs.get("activity") == work)
        )
        authorized_no_work_details: bool = user and (
            not (user.company or attrs.get("company"))
            or not (user.position or attrs.get("position"))
            or not (user.experience_years or attrs.get("experience_years"))
        )
        if anonymous_working and anonymous_no_work_details:
            return APPLICATION_ACTIVITY_ANONYMOUS_ERROR
        if authorized_working and authorized_no_work_details:
            return APPLICATION_ACTIVITY_AUTHORIZED_ERROR
        return None

    @staticmethod
    def check_specializations(
        attrs: dict[str, Any], user: SimpleLazyObject | None
    ) -> None:
        """
        Checks that authenticated user specified specializations in the profile
        or in the application.
        """
        if user and not (user.specializations.all() or attrs.get("specializations")):
            return APPLICATION_SPECIALIZATIONS_REQUIRED_ERROR
        return None

    def validate(self, attrs):
        """
        Validates format, email, phone, telegram, activity and specializations.
        Replaces the format with the correct one if the event has a strict format.
        """
        user: SimpleLazyObject | None = (
            self.context["request"].user
            if isinstance(self.context["request"].user, User)
            else None
        )

        format_error: str | None = self.__class__.check_format(attrs)
        if format_error:
            raise serializers.ValidationError(format_error)
        if attrs["event"].format != Event.FORMAT_HYBRID:
            attrs["format"] = attrs["event"].format

        email_error: str | None = self.__class__.check_email(attrs, user)
        if email_error:
            raise serializers.ValidationError(email_error)

        phone_error: str | None = self.__class__.check_phone(attrs, user)
        if phone_error:
            raise serializers.ValidationError(phone_error)

        telegram_error: str | None = self.__class__.check_telegram(attrs, user)
        if telegram_error:
            raise serializers.ValidationError(telegram_error)

        activity_error: str | None = self.__class__.check_activity(attrs, user)
        if activity_error:
            raise serializers.ValidationError(activity_error)

        specializations_error: str | None = self.__class__.check_specializations(
            attrs, user
        )
        if specializations_error:
            raise serializers.ValidationError(specializations_error)

        return attrs


class ApplicationCreateAnonymousSerializer(ApplicationCreateAuthorizedSerializer):
    """Serializer to create applications on behalf of anonymous site visitors."""

    first_name = serializers.CharField(
        max_length=Application._meta.get_field("first_name").max_length,
        label=Application._meta.get_field("first_name").verbose_name,
    )
    last_name = serializers.CharField(
        max_length=Application._meta.get_field("last_name").max_length,
        label=Application._meta.get_field("last_name").verbose_name,
    )
    activity = serializers.ChoiceField(
        choices=User.ACTIVITY_CHOISES,
        label=Application._meta.get_field("activity").verbose_name,
    )
    specializations = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(), many=True
    )


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for NotificationSettings."""

    class Meta:
        model = NotificationSettings
        fields = [
            "id",
            "user",
            "application",
            "email_notifications",
            "sms_notifications",
            "telegram_notifications",
            "phone_call_notifications",
        ]

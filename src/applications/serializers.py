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

APPLICATION_FORMAT_REQUIRED_ERROR: str = (
    "Если мероприятие имеет гибридный формат, в заявке обязательно должен быть указан "
    "желаемый формат участия."
)

# TODO: если мероприятие имеет строгий формат, то клиенту не нужно показывать чекбоксы
# с желаемым форматом участия - довести это до фронтов и дизайнеров.

# TODO: Неавторизованный заполняет поля first_name, last_name, email, phone, telegram
# (необязательное), birth_date (необязательное), city (необязательное), activity,
# company (необязательное, если он не работает), position (необязательное, если он не
# работает), experience_years (необязательное, если он не работает), specializations
# (обязательное)

# TODO: У авторизованного нужно проверять, что заполнено specializations в ЛК
# либо кидать ошибку валидации (просить заполнить в ЛК или указать в заявке).
# А в activity у него сразу после регистрации будет значение по дефолту - работаю,
# но он его может поменять в ЛК. Если у него activity=работаю, то просим при подаче
# заявки указать место, должность и число лет опыта (валидация на уровне апи).

# TODO: # если activity=working, то в заявке поля company, position, experience_years
# становятся обязательными для анонима. Если у авторизованного activity=working, а в ЛК
# и в самой заявке не указаны company, position, experience_years, то тоже просим его их
# заполнить в заявке или в ЛК (не создаем ему заявку, пока он их не заполнит)


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

    # TODO: refactoring вынести проверки в отдельные функции, а отсюда их вызывать
    def validate(self, attrs):
        """
        Checks that attrs include a format field if the event has a hybrid format.
        Replaces the format with the correct one if the event has a strict format.
        Checks email, phone, telegram.
        """
        # format check and replacement
        if attrs["event"].format == Event.FORMAT_HYBRID and not attrs.get("format"):
            raise serializers.ValidationError(APPLICATION_FORMAT_REQUIRED_ERROR)
        if attrs["event"].format != Event.FORMAT_HYBRID:
            attrs["format"] = attrs["event"].format

        # git user for email, phone and telegram checks
        user: SimpleLazyObject | None = (
            self.context["request"].user
            if isinstance(self.context["request"].user, User)
            else None
        )

        # email checks
        another_user_email_error: str | None = check_another_user_email(
            user=user, email=attrs.get("email")
        )
        if another_user_email_error:
            raise serializers.ValidationError(another_user_email_error)
        if (
            attrs.get("email")
            and Application.objects.filter(
                event=attrs["event"], email=attrs["email"]
            ).exists()
        ):
            raise serializers.ValidationError(APPLICATION_EVENT_EMAIL_UNIQUE_ERROR)

        # phone checks
        another_user_phone_error: str | None = check_another_user_phone(
            user=user, phone=attrs.get("phone")
        )
        if another_user_phone_error:
            raise serializers.ValidationError(another_user_phone_error)
        if (
            attrs.get("phone")
            and Application.objects.filter(
                event=attrs["event"], phone=attrs["phone"]
            ).exists()
        ):
            raise serializers.ValidationError(APPLICATION_EVENT_PHONE_UNIQUE_ERROR)

        # telegram checks
        another_user_telegram_error: str | None = check_another_user_telegram(
            user=user, telegram=attrs.get("telegram")
        )
        if another_user_telegram_error:
            raise serializers.ValidationError(another_user_telegram_error)
        if (
            attrs.get("telegram")
            and Application.objects.filter(
                event=attrs["event"], telegram=attrs["telegram"]
            ).exists()
        ):
            raise serializers.ValidationError(APPLICATION_EVENT_TELEGRAM_UNIQUE_ERROR)

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

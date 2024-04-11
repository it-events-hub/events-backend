from typing import Any

from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from .models import Application, NotificationSettings
from .utils import (
    APPLICATION_ACTIVITY_ANONYMOUS_ERROR,
    APPLICATION_ACTIVITY_AUTHORIZED_ERROR,
    APPLICATION_EVENT_CLOSED_ERROR,
    APPLICATION_EVENT_EMAIL_UNIQUE_ERROR,
    APPLICATION_EVENT_IS_DELETED_ERROR,
    APPLICATION_EVENT_OFFLINE_CLOSED_ERROR,
    APPLICATION_EVENT_ONLINE_CLOSED_ERROR,
    APPLICATION_EVENT_PHONE_UNIQUE_ERROR,
    APPLICATION_EVENT_STARTTIME_ERROR,
    APPLICATION_EVENT_TELEGRAM_UNIQUE_ERROR,
    APPLICATION_FORMAT_REQUIRED_ERROR,
    APPLICATION_SPECIALIZATIONS_REQUIRED_ERROR,
    APPLICATION_USER_ALREADY_REGISTERED_ERROR,
    NOTIFICATION_SETTINGS_ID_FIELD_LABEL,
    check_another_user_email,
    check_another_user_phone,
    check_another_user_telegram,
)
from api.loggers import logger
from events.models import Event
from users.models import Specialization, User
from users.utils import PHONE_NUMBER_REGEX, check_birth_date


class ApplicationCreateAuthorizedSerializer(serializers.ModelSerializer):
    """Serializer to create applications on behalf of authorized site visitors."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    activity = serializers.ChoiceField(
        choices=User.ACTIVITY_CHOISES,
        label=Application._meta.get_field("activity").verbose_name,
        required=False,
    )
    notification_settings_id = serializers.SerializerMethodField(
        label=NOTIFICATION_SETTINGS_ID_FIELD_LABEL
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
            "notification_settings_id",
        ]

    def get_notification_settings_id(self, obj) -> int:
        """Shows object NotificationSettings ID."""
        if obj.user:
            return obj.user.notification_settings.id
        return obj.notification_settings.id

    def validate_birth_date(self, value):
        """Validates birth date."""
        birth_date_error: str | None = check_birth_date(value)
        if birth_date_error:
            raise ValidationError(birth_date_error)
        return value

    def validate_application_event_start_time(
        self, event: Event
    ) -> ValidationError | None:
        """
        Checks that the application has not been submitted for an event
        that has already started.
        """
        if event.start_time < timezone.now():
            raise ValidationError(APPLICATION_EVENT_STARTTIME_ERROR)

    def validate_application_event_is_deleted(
        self, event: Event
    ) -> ValidationError | None:
        """Checks that the application has not been submitted for deactivated event."""
        if event.is_deleted:
            raise ValidationError(APPLICATION_EVENT_IS_DELETED_ERROR)

    def validate_application_format(
        self, event: Event, attrs: dict[str, Any]
    ) -> ValidationError | None:
        """
        Checks that attrs include a format field if the event has a hybrid format.
        Replaces the format with the correct one if the event has a strict format.
        Checks that registration for the event is open for the format
        specified in the application.
        """
        if attrs["event"].format == Event.FORMAT_HYBRID and not attrs.get("format"):
            raise ValidationError(APPLICATION_FORMAT_REQUIRED_ERROR)

        if event.format != Event.FORMAT_HYBRID:
            attrs["format"] = event.format
            logger.debug(
                f"The format of application to event {event} has been changed to "
                f"{event.format}"
            )

        if attrs["event"].status == Event.STATUS_CLOSED:
            raise ValidationError(APPLICATION_EVENT_CLOSED_ERROR)
        if (
            attrs["event"].status == Event.STATUS_OFFLINE_CLOSED
            and attrs["format"] == Event.FORMAT_OFFLINE
        ):
            raise ValidationError(APPLICATION_EVENT_OFFLINE_CLOSED_ERROR)
        if (
            attrs["event"].status == Event.STATUS_ONLINE_CLOSED
            and attrs["format"] == Event.FORMAT_ONLINE
        ):
            raise ValidationError(APPLICATION_EVENT_ONLINE_CLOSED_ERROR)

    def validate_application_user(
        self, user: SimpleLazyObject | None, event: Event
    ) -> ValidationError | None:
        """Checks that the user has not registered twice for the same event."""
        if user and user.applications.filter(event=event).exists():
            raise ValidationError(APPLICATION_USER_ALREADY_REGISTERED_ERROR)

    def validate_application_email(
        self, attrs: dict[str, Any], user: SimpleLazyObject | None
    ) -> ValidationError | None:
        """
        Checks that the email does not belong to another user and that
        there is no application for the same event with the same email.
        """
        another_user_email_error: str | None = check_another_user_email(
            user=user, email=attrs.get("email")
        )
        if another_user_email_error:
            raise ValidationError(another_user_email_error)
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
            raise ValidationError(APPLICATION_EVENT_EMAIL_UNIQUE_ERROR)

    def validate_application_phone(
        self, attrs: dict[str, Any], user: SimpleLazyObject | None
    ) -> ValidationError | None:
        """
        Checks that the phone does not belong to another user and that
        there is no application for the same event with the same phone.
        """
        another_user_phone_error: str | None = check_another_user_phone(
            user=user, phone=attrs.get("phone")
        )
        if another_user_phone_error:
            raise ValidationError(another_user_phone_error)
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
            raise ValidationError(APPLICATION_EVENT_PHONE_UNIQUE_ERROR)

    def validate_application_telegram(
        self, attrs: dict[str, Any], user: SimpleLazyObject | None
    ) -> ValidationError | None:
        """
        Checks that the telegram does not belong to another user and that
        there is no application for the same event with the same telegram.
        """
        another_user_telegram_error: str | None = check_another_user_telegram(
            user=user, telegram=attrs.get("telegram")
        )
        if another_user_telegram_error:
            raise ValidationError(another_user_telegram_error)
        same_telegram_in_attrs: bool = bool(
            attrs.get("telegram") is not None
            and Application.objects.filter(
                event=attrs["event"], phone=attrs.get("telegram")
            ).exists()
        )
        same_telegram_in_user_personal_data: bool = bool(
            user
            and user.telegram
            and attrs.get("telegram") is None
            and Application.objects.filter(
                event=attrs["event"], telegram=user.telegram
            ).exists()
        )
        if same_telegram_in_attrs or same_telegram_in_user_personal_data:
            raise ValidationError(APPLICATION_EVENT_TELEGRAM_UNIQUE_ERROR)

    def validate_application_activity(
        self, attrs: dict[str, Any], user: SimpleLazyObject | None
    ) -> ValidationError | None:
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
            raise ValidationError(APPLICATION_ACTIVITY_ANONYMOUS_ERROR)
        if authorized_working and authorized_no_work_details:
            raise ValidationError(APPLICATION_ACTIVITY_AUTHORIZED_ERROR)

    def validate_application_specializations(
        self, attrs: dict[str, Any], user: SimpleLazyObject | None
    ) -> ValidationError | None:
        """
        Checks that authenticated user specified specializations in the profile
        or in the application.
        """
        if user and not (user.specializations.all() or attrs.get("specializations")):
            raise ValidationError(APPLICATION_SPECIALIZATIONS_REQUIRED_ERROR)

    def validate(self, attrs):
        """
        Validates start_time, format, user, email, phone, telegram, activity and
        specializations.
        """
        user: SimpleLazyObject | None = (
            self.context["request"].user
            if isinstance(self.context["request"].user, User)
            else None
        )
        event: Event = attrs["event"]

        self.validate_application_event_start_time(event)
        self.validate_application_event_is_deleted(event)
        self.validate_application_format(event, attrs)
        self.validate_application_user(user, event)
        self.validate_application_email(attrs, user)
        self.validate_application_phone(attrs, user)
        self.validate_application_telegram(attrs, user)
        self.validate_application_activity(attrs, user)
        self.validate_application_specializations(attrs, user)

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
    email = serializers.EmailField(
        max_length=Application._meta.get_field("email").max_length,
        label=Application._meta.get_field("email").verbose_name,
    )
    phone = serializers.RegexField(
        max_length=Application._meta.get_field("phone").max_length,
        label=Application._meta.get_field("phone").verbose_name,
        regex=PHONE_NUMBER_REGEX,
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

    user = serializers.PrimaryKeyRelatedField(
        read_only=True, label=NotificationSettings._meta.get_field("user").verbose_name
    )
    application = serializers.PrimaryKeyRelatedField(
        read_only=True,
        label=NotificationSettings._meta.get_field("application").verbose_name,
    )
    telegram_present = serializers.SerializerMethodField()

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
            "telegram_present",
        ]

    def get_telegram_present(self, obj) -> bool:
        """
        Shows whether Telegram is present in the data of registrated user or
        in the application of anonymous visitor.
        """
        if obj.user:
            return bool(obj.user.telegram)
        return bool(obj.application.telegram)


class DestroyObjectSuccessSerializer(serializers.Serializer):
    """Serializer to provide some json response after objects deletion."""

    message = serializers.CharField()

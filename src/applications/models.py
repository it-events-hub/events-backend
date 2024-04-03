from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from events.models import Event
from users.models import (
    BIRTH_DATE_TOO_OLD_ERROR_MESSAGE,
    BIRTH_DATE_TOO_YOUNG_ERROR_MESSAGE,
    MAX_EXPERIENCE_YEARS,
    MAX_USER_AGE,
    MIN_USER_AGE,
    PHONE_NUMBER_ERROR,
    PHONE_NUMBER_REGEX,
    TELEGRAM_ID_ERROR,
    TELEGRAM_ID_REGEX,
    Specialization,
    User,
)


class Source(models.Model):
    """Model for sources of information about events."""

    name = models.CharField("Название", max_length=40, unique=True)
    slug = models.SlugField("Слаг", max_length=40, unique=True)

    class Meta:
        verbose_name = "Источник информации"
        verbose_name_plural = "Источники информации"

    def __str__(self) -> str:
        return self.name


class Application(models.Model):
    """Model for storing applications for participation in an event."""

    STATUS_SUBMITTED: str = "submitted"
    STATUS_REVIEWED: str = "reviewed"
    STATUS_APPROVED: str = "approved"
    STATUS_REJECTED: str = "rejected"

    FORMAT_CHOISES: list[tuple[str]] = [
        (STATUS_SUBMITTED, "подана"),
        (STATUS_REVIEWED, "рассмотрена"),
        (STATUS_APPROVED, "одобрена"),
        (STATUS_REJECTED, "отклонена"),
    ]

    status = models.CharField(
        "Статус", max_length=9, choices=FORMAT_CHOISES, default=STATUS_SUBMITTED
    )
    event = models.ForeignKey(
        Event,
        related_name="applications",
        on_delete=models.CASCADE,
        verbose_name="Мероприятие",
    )
    source = models.ForeignKey(
        Source,
        related_name="applications",
        on_delete=models.SET_DEFAULT,
        default="deleted source",
        verbose_name="Источник информации",
    )
    user = models.ForeignKey(
        User,
        related_name="applications",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        blank=True,
        null=True,
    )
    first_name = models.CharField("Имя", max_length=40)
    last_name = models.CharField("Фамилия", max_length=40)
    email = models.EmailField("Электронная почта", max_length=100)
    phone = models.CharField(
        "Телефон",
        validators=[
            RegexValidator(regex=PHONE_NUMBER_REGEX, message=PHONE_NUMBER_ERROR)
        ],
        max_length=20,
    )
    telegram = models.CharField(
        "Телеграм ID",
        max_length=33,
        validators=[
            RegexValidator(regex=TELEGRAM_ID_REGEX, message=TELEGRAM_ID_ERROR),
        ],
        blank=True,
        null=True,
    )
    birth_date = models.DateField("Дата рождения", blank=True, null=True)
    city = models.CharField("Город", max_length=40, blank=True, null=True)
    activity = models.CharField(
        "Род занятий",
        max_length=20,
        choices=User.ACTIVITY_CHOISES,
        default=User.ACTIVITY_WORK,
    )
    company = models.CharField("Место работы", max_length=50, blank=True, null=True)
    position = models.CharField("Должность", max_length=100, blank=True, null=True)
    experience_years = models.PositiveSmallIntegerField(
        "Опыт работы в годах",
        validators=[MaxValueValidator(MAX_EXPERIENCE_YEARS)],
        blank=True,
        null=True,
    )
    specializations = models.ManyToManyField(
        Specialization, related_name="applications", blank=True
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def clean_fields(self, exclude=None):
        """Checks the user's birth date."""
        super().clean_fields(exclude=exclude)
        now = timezone.now()
        if (
            self.birth_date
            and self.birth_date + relativedelta(years=MIN_USER_AGE) > now.date()
        ):
            raise ValidationError(BIRTH_DATE_TOO_YOUNG_ERROR_MESSAGE)
        if (
            self.birth_date
            and self.birth_date + relativedelta(years=MAX_USER_AGE) < now.date()
        ):
            raise ValidationError(BIRTH_DATE_TOO_OLD_ERROR_MESSAGE)

    def __str__(self) -> str:
        if self.user:
            return f"{self.event.name} {self.user.email}"
        return f"{self.event.name} {self.email}"


# TODO: check that user or application is NULL, not both
class NotificationSettings(models.Model):
    """Model for storing event notification settings."""

    NOTIFY_DAY_BEFORE: str = "day before"
    NOTIFY_HOUR_BEFORE: str = "hour before"
    NOTIFY_15_MINUTES_BEFORE: str = "15 minutes before"

    NOTIFY_CHOISES: list[tuple[str]] = [
        (NOTIFY_DAY_BEFORE, "За день"),
        (NOTIFY_HOUR_BEFORE, "За час"),
        (NOTIFY_15_MINUTES_BEFORE, "За 15 минут"),
    ]

    user = models.OneToOneField(
        User,
        related_name="notification_settings",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        blank=True,
        null=True,
    )
    application = models.OneToOneField(
        Application,
        related_name="notification_settings",
        on_delete=models.CASCADE,
        verbose_name="Заявка",
        blank=True,
        null=True,
    )
    email_notifications = models.CharField(
        "На почту", max_length=17, choices=NOTIFY_CHOISES, blank=True, null=True
    )
    sms_notifications = models.CharField(
        "По СМС", max_length=17, choices=NOTIFY_CHOISES, blank=True, null=True
    )
    telegram_notifications = models.CharField(
        "В телеграм", max_length=17, choices=NOTIFY_CHOISES, blank=True, null=True
    )
    phone_call_notifications = models.CharField(
        "Позвонить", max_length=17, choices=NOTIFY_CHOISES, blank=True, null=True
    )

    class Meta:
        verbose_name = "Настройки уведомлений"
        verbose_name_plural = "Настройки уведомлений"

    def __str__(self) -> str:
        if self.user:
            return f"Notification settings for {self.user}"
        return f"Notification settings for {self.application}"


class Notification(models.Model):
    """
    Model for storing notification celery task_id related to a specific application.
    """

    task_id = models.CharField("ID задачи", max_length=255, unique=True)
    application = models.ForeignKey(
        Application,
        related_name="notifications",
        on_delete=models.CASCADE,
        verbose_name="Заявка",
    )

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self) -> str:
        return f"{self.task_id} {self.application}"

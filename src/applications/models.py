from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint
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

APPLICATION_ANONYMOUS_REQUIRED_FIELDS_ERROR: str = (
    "Если заявка подается от имени анонимного посетителя, в ней должны быть указаны "
    "имя, фамилия, емейл, телефон и род деятельности."
)
APPLICATION_FORMAT_ERROR: str = (
    "Формат участия в заявке не соответствует формату проведения мероприятия."
)
APPLICATION_EMAIL_ERROR: str = (
    "Этот адрес электронной почты принадлежит другому пользователю."
)
APPLICATION_PHONE_ERROR: str = "Этот номер телефона принадлежит другому пользователю."
APPLICATION_TELEGRAM_ERROR: str = "Этот Telegram ID принадлежит другому пользователю."
APPLICATION_EVENT_TELEGRAM_UNIQUE_ERROR: str = (
    "Заявка на данное мероприятие от пользователя с таким Telegram ID уже существует."
)
NOTIFICATION_SETTINGS_APPLICATION_OF_USER_ERROR: str = (
    "Если заявка принадлежит зарегистрированному пользователю, настройки уведомлений "
    "должны быть привязаны к этому пользователю, а не к его отдельным заявкам."
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


# TODO: сейчас в заявке автоматически заполняются поля зарегистрированного юзера,
# кроме его specializations, там связь многие-ко-многим, и обновления почему-то
# не сохраняются в БД, даже если создавать их в методе save. Поэтому нужно автозаполнять
# и обновлять specializations на уровне апи.
# TODO: При внесении изменений в данные профиля нужно будет обновлять их и во всех
# заявках данного пользователя (заявки на мероприятия, где is_event_started=False),
# это тоже будет на уровне апи, включая изменения specializations.
# TODO: activity обязательный, хотя у зареганного юзера он всегда будет указан из-за
# дефолтного значения.
class Application(models.Model):
    """Model for storing applications for participation in events."""

    STATUS_SUBMITTED: str = "submitted"
    STATUS_REVIEWED: str = "reviewed"
    STATUS_APPROVED: str = "approved"
    STATUS_REJECTED: str = "rejected"

    STATUS_CHOISES: list[tuple[str]] = [
        (STATUS_SUBMITTED, "подана"),
        (STATUS_REVIEWED, "рассмотрена"),
        (STATUS_APPROVED, "одобрена"),
        (STATUS_REJECTED, "отклонена"),
    ]

    FORMAT_CHOISES: list[tuple[str]] = [
        (Event.FORMAT_ONLINE, "онлайн"),
        (Event.FORMAT_OFFLINE, "офлайн"),
    ]

    status = models.CharField(
        "Статус", max_length=9, choices=STATUS_CHOISES, default=STATUS_SUBMITTED
    )
    event = models.ForeignKey(
        Event,
        related_name="applications",
        on_delete=models.CASCADE,
        verbose_name="Мероприятие",
    )
    format = models.CharField(
        "Формат участия",
        max_length=7,
        choices=FORMAT_CHOISES,
        default=Event.FORMAT_ONLINE,
    )
    is_event_started = models.BooleanField("Мероприятие началось", default=False)
    source = models.ForeignKey(
        Source,
        related_name="applications",
        on_delete=models.SET_NULL,
        verbose_name="Источник информации",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User,
        related_name="applications",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        blank=True,
        null=True,
    )
    first_name = models.CharField("Имя", max_length=40, blank=True, null=True)
    last_name = models.CharField("Фамилия", max_length=40, blank=True, null=True)
    email = models.EmailField(
        "Электронная почта", max_length=100, blank=True, null=True
    )
    phone = models.CharField(
        "Телефон",
        validators=[
            RegexValidator(regex=PHONE_NUMBER_REGEX, message=PHONE_NUMBER_ERROR)
        ],
        max_length=20,
        blank=True,
        null=True,
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
        "Род занятий", max_length=20, choices=User.ACTIVITY_CHOISES
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
        constraints = [
            UniqueConstraint(fields=["event", "email"], name="unique_event_email"),
            UniqueConstraint(fields=["event", "phone"], name="unique_event_phone"),
            CheckConstraint(
                check=Q(user__isnull=False)
                | (
                    Q(user__isnull=True)
                    & ~Q(first_name__isnull=True)
                    & ~Q(last_name__isnull=True)
                    & ~Q(email__isnull=True)
                    & ~Q(phone__isnull=True)
                    & ~Q(activity__isnull=True)
                ),
                name="check_user_or_details_filled",
                violation_error_message=APPLICATION_ANONYMOUS_REQUIRED_FIELDS_ERROR,
            ),
        ]

    def check_birth_date(self):
        """Checks the user's birth date."""
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

    def check_format(self):
        """Checks the application format and the event format match each other."""
        if (
            self.event.format != Event.FORMAT_HYBRID
            and self.event.format != self.format
        ):
            raise ValidationError(APPLICATION_FORMAT_ERROR)

    def check_email(self):
        """Checks that the email does not belong to another user."""
        if (
            self.user
            and User.objects.exclude(pk=self.user.pk).filter(email=self.email).exists()
        ):
            raise ValidationError(APPLICATION_EMAIL_ERROR)
        if not self.user and User.objects.filter(email=self.email).exists():
            raise ValidationError(APPLICATION_EMAIL_ERROR)

    def check_phone(self):
        """Checks that the phone does not belong to another user."""
        if (
            self.user
            and User.objects.exclude(pk=self.user.pk).filter(phone=self.phone).exists()
        ):
            raise ValidationError(APPLICATION_PHONE_ERROR)
        if not self.user and User.objects.filter(phone=self.phone).exists():
            raise ValidationError(APPLICATION_PHONE_ERROR)

    def check_telegram(self):
        """
        Checks that the telegram does not belong to another user.
        Checks that there is no application with the same event and telegram.
        """
        if (
            self.user
            and self.telegram
            and User.objects.exclude(pk=self.user.pk)
            .filter(telegram=self.telegram)
            .exists()
        ):
            raise ValidationError(APPLICATION_TELEGRAM_ERROR)
        if (
            not self.user
            and self.telegram
            and User.objects.filter(telegram=self.telegram).exists()
        ):
            raise ValidationError(APPLICATION_TELEGRAM_ERROR)
        if (
            self.telegram
            and Application.objects.exclude(pk=self.pk)
            .filter(event=self.event, telegram=self.telegram)
            .exists()
        ):
            raise ValidationError(APPLICATION_EVENT_TELEGRAM_UNIQUE_ERROR)

    def autofill_fields(self):
        """
        Fills in the fields of an application of a registered user,
        except for the user's specializations.
        """
        self.first_name = self.user.first_name
        self.last_name = self.user.last_name
        self.email = self.user.email
        self.phone = self.user.phone
        self.telegram = self.user.telegram
        self.birth_date = self.user.birth_date
        self.city = self.user.city
        self.activity = self.user.activity
        self.company = self.user.company
        self.position = self.user.position
        self.experience_years = self.user.experience_years

    def clean(self):
        """
        Checks and triggers automatic filling of application fields if it is submitted
        by an authenticated user.
        Updates user data, if it was changed in the application.
        """
        user_data: list[str] = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "telegram": self.telegram,
            "birth_date": self.birth_date,
            "city": self.city,
            "activity": self.activity,
            "company": self.company,
            "position": self.position,
            "experience_years": self.experience_years,
        }
        self.check_birth_date()
        self.check_format()
        self.check_email()
        self.check_phone()
        self.check_telegram()
        if self.user and any(user_data):
            for key, value in user_data.items():
                if value:
                    setattr(self.user, key, value)
            self.user.save()  # обновляем информацию пользователя кроме specializations
            self.autofill_fields()  # автоматически заполняем поля заявки

    def __str__(self) -> str:
        if self.user:
            return f"{self.event.name} {self.user.email}"
        return f"{self.event.name} {self.email}"


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
        constraints = [
            CheckConstraint(
                check=Q(user__isnull=False) | Q(application__isnull=False),
                name="check_user_or_application_fields_are_filled",
            ),
            CheckConstraint(
                check=~(Q(user__isnull=False) & Q(application__isnull=False)),
                name="check_user_or_application_fields_are_filled_but_not_both",
            ),
        ]

    def clean(self):
        """
        Checks that notification settings are linked to applications without users.
        """
        if self.application and self.application.user:
            raise ValidationError(NOTIFICATION_SETTINGS_APPLICATION_OF_USER_ERROR)

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

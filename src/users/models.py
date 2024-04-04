from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from .managers import MyUserManager

MAX_EXPERIENCE_YEARS: int = 100
MIN_USER_AGE: int = 16
MAX_USER_AGE: int = 110
BIRTH_DATE_TOO_YOUNG_ERROR_MESSAGE: str = (
    "Указана неверная дата рождения, "
    f"пользователю должно быть не менее {MIN_USER_AGE} лет."
)
BIRTH_DATE_TOO_OLD_ERROR_MESSAGE: str = (
    "Указана неверная дата рождения, "
    f"пользователю должно быть не более {MAX_USER_AGE} лет."
)
PHONE_NUMBER_ERROR: str = (
    "Введен некорректный номер телефона. Введите номер телефона в "
    "форматах '+7XXXXXXXXXX', '7XXXXXXXXXX' или '8XXXXXXXXXX'."
)
PHONE_NUMBER_REGEX: str = r"^(\+7|7|8)\d{10}$"
TELEGRAM_ID_ERROR: str = (
    "Значение должно начинаться с символа @, затем идет username длиной 5-32 символа, "
    "в котором допускаются только латинские буквы, цифры и нижнее подчеркивание."
)
TELEGRAM_ID_REGEX: str = r"^@[a-zA-Z0-9_]{5,32}$"


class Specialization(models.Model):
    """Model for IT directions."""

    name = models.CharField("Название", max_length=40, unique=True)
    slug = models.SlugField("Слаг", max_length=40, unique=True)

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"

    def __str__(self) -> str:
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """Custom model for users."""

    ACTIVITY_WORK: str = "working"
    ACTIVITY_STUDY: str = "studying"
    ACTIVITY_SEEK: str = "job seeking"

    ACTIVITY_CHOISES: list[tuple[str]] = [
        (ACTIVITY_WORK, "работаю"),
        (ACTIVITY_STUDY, "учусь"),
        (ACTIVITY_SEEK, "в поиске работы"),
    ]

    first_name = models.CharField("Имя", max_length=40)
    last_name = models.CharField("Фамилия", max_length=40)
    email = models.EmailField("Электронная почта", unique=True, max_length=100)
    phone = models.CharField(
        "Телефон",
        unique=True,
        validators=[
            RegexValidator(regex=PHONE_NUMBER_REGEX, message=PHONE_NUMBER_ERROR)
        ],
        max_length=20,
    )
    telegram = models.CharField(
        "Телеграм ID",
        unique=True,
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
        "Род занятий", max_length=20, choices=ACTIVITY_CHOISES, default=ACTIVITY_WORK
    )
    company = models.CharField("Место работы", max_length=50, blank=True, null=True)
    position = models.CharField("Должность", max_length=100, blank=True, null=True)
    experience_years = models.PositiveSmallIntegerField(
        "Опыт работы в годах",
        validators=[MaxValueValidator(MAX_EXPERIENCE_YEARS)],
        blank=True,
        null=True,
    )
    is_staff = models.BooleanField("Сотрудник", default=False)
    is_active = models.BooleanField("Активирован", default=False)
    date_joined = models.DateTimeField("Дата и время регистрации", default=timezone.now)
    specializations = models.ManyToManyField(
        Specialization, related_name="users", blank=True
    )

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

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
        return f"{self.first_name} {self.last_name}".strip()

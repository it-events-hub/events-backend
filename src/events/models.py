from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .utils import EVENT_ENDTIME_ERROR, EVENT_PART_STARTTIME_ERROR
from users.models import Specialization


class EventType(models.Model):
    """Model for types of events."""

    name = models.CharField("Название", max_length=40, unique=True)
    slug = models.SlugField("Слаг", max_length=40, unique=True)

    class Meta:
        verbose_name = "Тип мероприятия"
        verbose_name_plural = "Типы мероприятий"

    def __str__(self) -> str:
        return self.name


class Speaker(models.Model):
    """Model for speakers."""

    name = models.CharField("ФИО", max_length=100, unique=True)
    company = models.CharField("Место работы", max_length=50)
    position = models.CharField("Должность", max_length=100)
    description = models.TextField("Регалии", blank=True)
    photo = models.ImageField("Фото", upload_to="speakers/", blank=True)

    class Meta:
        verbose_name = "Спикер"
        verbose_name_plural = "Спикеры"

    def __str__(self) -> str:
        return self.name


class Event(models.Model):
    """Model for events."""

    DEFAULT_EVENT_ORGANIZATOR: str = "Яндекс"

    FORMAT_OFFLINE: str = "offline"
    FORMAT_ONLINE: str = "online"
    FORMAT_HYBRID: str = "hybrid"

    FORMAT_CHOISES: list[tuple[str]] = [
        (FORMAT_OFFLINE, "офлайн"),
        (FORMAT_ONLINE, "онлайн"),
        (FORMAT_HYBRID, "офлайн и онлайн"),
    ]

    STATUS_OPEN: str = "registration is open"
    STATUS_OFFLINE_CLOSED: str = "registration offline is closed"
    STATUS_ONLINE_CLOSED: str = "registration online is closed"
    STATUS_CLOSED: str = "registration is closed"

    STATUS_CHOISES: list[tuple[str]] = [
        (STATUS_OPEN, "регистрация открыта"),
        (STATUS_OFFLINE_CLOSED, "регистрация офлайн закрыта"),
        (STATUS_ONLINE_CLOSED, "регистрация онлайн закрыта"),
        (STATUS_CLOSED, "регистрация закрыта"),
    ]

    name = models.CharField("Название", max_length=100, unique=True)
    organization = models.CharField(
        "Организатор", max_length=100, default=DEFAULT_EVENT_ORGANIZATOR
    )
    description = models.TextField("Описание")
    is_deleted = models.BooleanField("Деактивировано", default=False)
    status = models.CharField(
        "Статус", max_length=30, choices=STATUS_CHOISES, default=STATUS_OPEN
    )
    format = models.CharField(
        "Формат", max_length=7, choices=FORMAT_CHOISES, default=FORMAT_HYBRID
    )
    created = models.DateTimeField("Создано", default=timezone.now)
    start_time = models.DateTimeField("Время начала")
    end_time = models.DateTimeField("Время окончания", blank=True, null=True)
    cost = models.FloatField("Стоимость", default=0, validators=[MinValueValidator(0)])
    place = models.TextField("Место", blank=True)
    event_type = models.ForeignKey(
        EventType, related_name="events", on_delete=models.CASCADE, verbose_name="Тип"
    )
    specializations = models.ForeignKey(
        Specialization,
        related_name="events",
        on_delete=models.CASCADE,
        verbose_name="Направление",
    )
    participant_offline_limit = models.PositiveIntegerField(
        "Количество офлайн участников", blank=True, null=True
    )
    participant_online_limit = models.PositiveIntegerField(
        "Количество онлайн участников", blank=True, null=True
    )
    registration_deadline = models.DateTimeField(
        "Регистрация до", blank=True, null=True
    )
    livestream_link = models.URLField("Трансляция", blank=True, null=True)
    additional_materials_link = models.URLField(
        "Дополнительные материалы", blank=True, null=True
    )
    image = models.ImageField("Афиша", upload_to="events/", blank=True)
    is_featured = models.BooleanField("Продвигать на Главной", default=False)
    is_featured_on_yandex_afisha = models.BooleanField(
        "Продвигать на Яндекс Афише", default=False
    )

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def clean(self):
        """Checks that start_time is not later than end_time."""
        if self.start_time and self.end_time and self.start_time > self.end_time:
            raise ValidationError(EVENT_ENDTIME_ERROR)

    def __str__(self) -> str:
        return self.name


class EventPart(models.Model):
    """Model for agenda items within specific events."""

    event = models.ForeignKey(
        Event,
        related_name="parts",
        on_delete=models.CASCADE,
        verbose_name="Мероприятие",
    )
    is_deleted = models.BooleanField("Деактивировано", default=False)
    name = models.CharField("Название", max_length=100)
    description = models.TextField("Описание", blank=True, null=True)
    speaker = models.ForeignKey(
        Speaker,
        related_name="presentations",
        on_delete=models.CASCADE,
        verbose_name="Спикер",
        blank=True,
        null=True,
    )
    created = models.DateTimeField("Создано", default=timezone.now)
    start_time = models.DateTimeField("Время начала")
    presentation_type = models.CharField("Тип", max_length=100)

    class Meta:
        verbose_name = "Часть мероприятия"
        verbose_name_plural = "Части мероприятий"

    def clean_fields(self, exclude=None):
        """Checks that start_time is not earlier than the event start time."""
        super().clean_fields(exclude=exclude)
        if self.start_time and self.start_time < self.event.start_time:
            raise ValidationError(EVENT_PART_STARTTIME_ERROR)

    def __str__(self) -> str:
        return f"{self.name} {self.event} {self.start_time}"

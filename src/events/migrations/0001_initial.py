# Generated by Django 5.0.3 on 2024-04-03 08:20

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=40, unique=True, verbose_name="Название"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(max_length=40, unique=True, verbose_name="Слаг"),
                ),
            ],
            options={
                "verbose_name": "Тип мероприятия",
                "verbose_name_plural": "Типы мероприятий",
            },
        ),
        migrations.CreateModel(
            name="Speaker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, unique=True, verbose_name="ФИО"),
                ),
                (
                    "company",
                    models.CharField(max_length=50, verbose_name="Место работы"),
                ),
                (
                    "position",
                    models.CharField(max_length=100, verbose_name="Должность"),
                ),
                ("description", models.TextField(blank=True, verbose_name="Регалии")),
                (
                    "photo",
                    models.ImageField(
                        blank=True, upload_to="speakers/", verbose_name="Фото"
                    ),
                ),
            ],
            options={
                "verbose_name": "Спикер",
                "verbose_name_plural": "Спикеры",
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Название"
                    ),
                ),
                (
                    "organization",
                    models.CharField(
                        default="Яндекс", max_length=100, verbose_name="Организатор"
                    ),
                ),
                ("description", models.TextField(verbose_name="Описание")),
                (
                    "is_deleted",
                    models.BooleanField(default=False, verbose_name="Деактивировано"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("registration is open", "регистрация открыта"),
                            ("registration is closed", "регистрация закрыта"),
                        ],
                        default="registration is open",
                        max_length=22,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "format",
                    models.CharField(
                        choices=[("offline", "онлайн"), ("online", "офлайн")],
                        default="offline",
                        max_length=7,
                        verbose_name="Формат",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Создано"
                    ),
                ),
                ("start_time", models.DateTimeField(verbose_name="Время начала")),
                (
                    "end_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Время окончания"
                    ),
                ),
                (
                    "cost",
                    models.FloatField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Стоимость",
                    ),
                ),
                ("place", models.TextField(blank=True, verbose_name="Место")),
                (
                    "participant_limit",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Количество участников"
                    ),
                ),
                (
                    "registration_deadline",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Регистрация до"
                    ),
                ),
                (
                    "livestream_link",
                    models.URLField(blank=True, null=True, verbose_name="Трансляция"),
                ),
                (
                    "additional_materials_link",
                    models.URLField(
                        blank=True, null=True, verbose_name="Дополнительные материалы"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True, upload_to="events/", verbose_name="Афиша"
                    ),
                ),
                (
                    "is_featured",
                    models.BooleanField(
                        default=False, verbose_name="Продвигать на Главной"
                    ),
                ),
                (
                    "is_featured_on_yandex_afisha",
                    models.BooleanField(
                        default=False, verbose_name="Продвигать на Яндекс Афише"
                    ),
                ),
                (
                    "specializations",
                    models.ForeignKey(
                        default="deleted specialization",
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="events",
                        to="users.specialization",
                    ),
                ),
                (
                    "event_type",
                    models.ForeignKey(
                        default="deleted event",
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="events",
                        to="events.eventtype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Мероприятие",
                "verbose_name_plural": "Мероприятия",
            },
        ),
        migrations.CreateModel(
            name="EventPart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_deleted",
                    models.BooleanField(default=False, verbose_name="Деактивировано"),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Название")),
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Создано"
                    ),
                ),
                ("start_time", models.DateTimeField(verbose_name="Время начала")),
                (
                    "presentation_type",
                    models.CharField(max_length=100, verbose_name="Тип"),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="parts",
                        to="events.event",
                        verbose_name="Мероприятие",
                    ),
                ),
                (
                    "speaker",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="presentations",
                        to="events.speaker",
                        verbose_name="Спикер",
                    ),
                ),
            ],
            options={
                "verbose_name": "Часть мероприятия",
                "verbose_name_plural": "Части мероприятий",
            },
        ),
    ]

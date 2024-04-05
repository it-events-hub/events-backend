# Generated by Django 5.0.3 on 2024-04-05 10:32

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("events", "0001_initial"),
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Source",
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
                "verbose_name": "Источник информации",
                "verbose_name_plural": "Источники информации",
            },
        ),
        migrations.CreateModel(
            name="Application",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("submitted", "подана"),
                            ("reviewed", "рассмотрена"),
                            ("approved", "одобрена"),
                            ("rejected", "отклонена"),
                        ],
                        default="submitted",
                        max_length=9,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "format",
                    models.CharField(
                        choices=[("online", "онлайн"), ("offline", "офлайн")],
                        default="online",
                        max_length=7,
                        verbose_name="Формат участия",
                    ),
                ),
                (
                    "is_event_started",
                    models.BooleanField(
                        default=False, verbose_name="Мероприятие началось"
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=40, null=True, verbose_name="Имя"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=40, null=True, verbose_name="Фамилия"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Электронная почта",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Введен некорректный номер телефона. Введите номер телефона в форматах '+7XXXXXXXXXX', '7XXXXXXXXXX' или '8XXXXXXXXXX'.",
                                regex="^(\\+7|7|8)\\d{10}$",
                            )
                        ],
                        verbose_name="Телефон",
                    ),
                ),
                (
                    "telegram",
                    models.CharField(
                        blank=True,
                        max_length=33,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Значение должно начинаться с символа @, затем идет username длиной 5-32 символа, в котором допускаются только латинские буквы, цифры и нижнее подчеркивание.",
                                regex="^@[a-zA-Z0-9_]{5,32}$",
                            )
                        ],
                        verbose_name="Телеграм ID",
                    ),
                ),
                (
                    "birth_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Дата рождения"
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        blank=True, max_length=40, null=True, verbose_name="Город"
                    ),
                ),
                (
                    "activity",
                    models.CharField(
                        choices=[
                            ("working", "работаю"),
                            ("studying", "учусь"),
                            ("job seeking", "в поиске работы"),
                        ],
                        max_length=20,
                        verbose_name="Род занятий",
                    ),
                ),
                (
                    "company",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        verbose_name="Место работы",
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Должность"
                    ),
                ),
                (
                    "experience_years",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MaxValueValidator(100)],
                        verbose_name="Опыт работы в годах",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="events.event",
                        verbose_name="Мероприятие",
                    ),
                ),
                (
                    "specializations",
                    models.ManyToManyField(
                        blank=True,
                        related_name="applications",
                        to="users.specialization",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="applications",
                        to="applications.source",
                        verbose_name="Источник информации",
                    ),
                ),
            ],
            options={
                "verbose_name": "Заявка",
                "verbose_name_plural": "Заявки",
            },
        ),
        migrations.CreateModel(
            name="Notification",
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
                    "task_id",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="ID задачи"
                    ),
                ),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="applications.application",
                        verbose_name="Заявка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Уведомление",
                "verbose_name_plural": "Уведомления",
            },
        ),
        migrations.CreateModel(
            name="NotificationSettings",
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
                    "email_notifications",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("day before", "За день"),
                            ("hour before", "За час"),
                            ("15 minutes before", "За 15 минут"),
                        ],
                        max_length=17,
                        null=True,
                        verbose_name="На почту",
                    ),
                ),
                (
                    "sms_notifications",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("day before", "За день"),
                            ("hour before", "За час"),
                            ("15 minutes before", "За 15 минут"),
                        ],
                        max_length=17,
                        null=True,
                        verbose_name="По СМС",
                    ),
                ),
                (
                    "telegram_notifications",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("day before", "За день"),
                            ("hour before", "За час"),
                            ("15 minutes before", "За 15 минут"),
                        ],
                        max_length=17,
                        null=True,
                        verbose_name="В телеграм",
                    ),
                ),
                (
                    "phone_call_notifications",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("day before", "За день"),
                            ("hour before", "За час"),
                            ("15 minutes before", "За 15 минут"),
                        ],
                        max_length=17,
                        null=True,
                        verbose_name="Позвонить",
                    ),
                ),
                (
                    "application",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_settings",
                        to="applications.application",
                        verbose_name="Заявка",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_settings",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Настройки уведомлений",
                "verbose_name_plural": "Настройки уведомлений",
            },
        ),
        migrations.AddConstraint(
            model_name="notificationsettings",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("user__isnull", False),
                    ("application__isnull", False),
                    _connector="OR",
                ),
                name="check_user_or_application_fields_are_filled",
            ),
        ),
        migrations.AddConstraint(
            model_name="notificationsettings",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("user__isnull", False),
                    ("application__isnull", False),
                    _negated=True,
                ),
                name="check_user_or_application_fields_are_filled_but_not_both",
            ),
        ),
        migrations.AddConstraint(
            model_name="application",
            constraint=models.UniqueConstraint(
                fields=("event", "email"), name="unique_event_email"
            ),
        ),
        migrations.AddConstraint(
            model_name="application",
            constraint=models.UniqueConstraint(
                fields=("event", "phone"), name="unique_event_phone"
            ),
        ),
        migrations.AddConstraint(
            model_name="application",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("user__isnull", False),
                    models.Q(
                        ("user__isnull", True),
                        models.Q(("first_name__isnull", True), _negated=True),
                        models.Q(("last_name__isnull", True), _negated=True),
                        models.Q(("email__isnull", True), _negated=True),
                        models.Q(("phone__isnull", True), _negated=True),
                        models.Q(("activity__isnull", True), _negated=True),
                    ),
                    _connector="OR",
                ),
                name="check_user_or_details_filled",
                violation_error_message="Если заявка подается от имени анонимного посетителя, в ней должны быть указаны имя, фамилия, емейл, телефон и род деятельности.",
            ),
        ),
    ]

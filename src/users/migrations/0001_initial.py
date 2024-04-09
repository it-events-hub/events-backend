# Generated by Django 5.0.3 on 2024-04-02 12:14

import django.core.validators
import django.utils.timezone
from django.db import migrations, models

import users.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Specialization",
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
                "verbose_name": "Направление",
                "verbose_name_plural": "Направления",
            },
        ),
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("first_name", models.CharField(max_length=40, verbose_name="Имя")),
                ("last_name", models.CharField(max_length=40, verbose_name="Фамилия")),
                (
                    "email",
                    models.EmailField(
                        max_length=100, unique=True, verbose_name="Электронная почта"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        max_length=20,
                        unique=True,
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
                        unique=True,
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
                        default="working",
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
                    "is_staff",
                    models.BooleanField(default=False, verbose_name="Сотрудник"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=False, verbose_name="Активирован"),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Дата и время регистрации",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
                (
                    "specializations",
                    models.ManyToManyField(
                        blank=True, related_name="users", to="users.specialization"
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
            managers=[
                ("objects", users.managers.MyUserManager()),
            ],
        ),
    ]

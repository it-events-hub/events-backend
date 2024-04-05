from rest_framework import serializers

from .models import Application
from users.models import Specialization, User

# TODO: поля status (бд дефолт, потом в админке), is_event_started (бд дефолт, потом
# celery beat), user (апи в perform_create определяет тип request.user, если он
# авторизован, то проставляет его, если неавторизован, то там должен быть NULL)
# не заполняются самим посетителем сайта.

# TODO: если мероприятие имеет гибридный формат, тогда поле format заполняет клиент,
# если формат мероприятия строгий (онлайн или офлайн), тогда формат должен автоматически
# проставляться сервером на уровне апи, а клиенту вообще не нужно показывать чекбоксы
# с желаемым форматом участия (довести это до фронтов и дизайнеров, пока на макете
# вообще нету желаемого формата участия, но макет еще поменяют). То есть на уровне БД
# format обязательное поле, на уровне апи наверно тоже сделаем обязательным, но в
# perform_create проверим формат самого мероприятия, и если он строгий - то записываем
# в поле format верный формат (независимо от указанного клиентом), а если гибрид, то
# значение, указанное клиентом (если не указал - показываем ошибку). Хотя в БД стоит по
# дефолту онлайн, возможно ошибка на уровне сериализатора появится раньше, чем сработает
# дефолтное значение из БД, а может и не будет никакой ошибки сериализатора и по дефолту
# будет поставлен онлайн

# TODO: Неавторизованный заполняет поля first_name, last_name, email, phone, telegram
# (необязательное), birth_date (необязательное), city (необязательное), activity,
# company (необязательное, если он не работает), position (необязательное, если он не
# работает), experience_years (необязательное, если он не работает), specializations
# (обязательное)

# TODO: если заявку подает аноним, то мы перед ее созданием проверяем, нет ли у нас в
# базе пользователя с такими же email, phone, telegram. Если они есть, то не создаем
# такую заявку, а выводим ему сообщение, что у нас на сайте зарегистрирован юзер с
# таким же email, phone, telegram, и просим авторизоваться на сайте перед подачей заявки
# Такую проверку нужно добавить и на уровень БД, а не только в апи (в БД готово).


# TODO: У авторизованного нужно проверять, что заполнено specializations в ЛК
# либо кидать ошибку валидации (просить заполнить в ЛК или указать в заявке).
# А в activity у него сразу после регистрации будет значение по дефолту - работаю,
# но он его может поменять в ЛК. Если у него activity=работаю, то просим при подаче
# заявки указать место, должность и число лет опыта (валидация на уровне апи).
class ApplicationCreateAuthorizedSerializer(serializers.ModelSerializer):
    """Serializer to create applications on behalf of authorized site visitors."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    format = serializers.ChoiceField(
        choices=Application.FORMAT_CHOISES,
        label=Application._meta.get_field("format").verbose_name,
    )
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
            "birth_date",  # нужна валидация на уровне апи, clean_fields не запускается
            "city",
            "activity",  # если working, company, position, experience_years обязательны
            "company",
            "position",
            "experience_years",
            "specializations",
        ]


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

from rest_framework import serializers

from .models import Application
from users.models import Specialization

# TODO: поля status (бд, потом в админке), is_event_started (бд, потом celery beat),
# user (апи автоматически определяет тип request.user, если он авторизован, то
# проставляет его, если неавторизован, то там должен быть NULL) проставляются
# автоматически в perform_create

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
# (необязательное), birth_date (необязательное), city (необязательное), activity
# (обязательное, но значение по дефолту - работаю, т.е. нужно прям прописать в
# сериализаторе его обязательность), company (необязательное), position
# (необязательное), experience_years (необязательное), specializations (обязательное)

# TODO: если заявку подает аноним, то мы перед ее созданием проверяем, нет ли у нас в
# базе пользователя с такими же email, phone, telegram. Если они есть, то не создаем
# такую заявку, а выводим ему сообщение, что у нас на сайте зарегистрирован юзер с
# таким же email, phone, telegram, и просим авторизоваться на сайте перед подачей заявки
# Такую проверку нужно добавить и на уровень БД, а не только в апи (в БД готово).

# TODO: У авторизованного уже точно заполнены first_name, last_name, email, phone, но
# могут отсутствовать данные по telegram, birth_date, city, company, position,
# experience_years, specializations. А в activity у него сразу после регистрации будет
# значение по дефолту - работаю, но он его может поменять в ЛК.
# Значит, он не сможет подать заявку, пока у него не заполнены в ЛК specializations.
# Ему будет высвечиваться ошибка, которая будет предлагать заполнить specializations
# в ЛК или вписать их прямо в заявку (и тогда они сохранятся в его профиле в
# БД). Это надо делать на уровне апи, на уровне БД в методе clean не выйдет, тем более
# этот метод не запускается при POST-запросе к апи, это надо настраивать валидацию в
# сериализаторе

# TODO: Поле source заполняют все (и аноним, и авторизованный), на уровне БД оно
# необязательное, на уровне апи тоже необязательное


class ApplicationCreateAnonymousSerializer(serializers.ModelSerializer):
    """Serializer to create applications on behalf of anonymous site visitors."""

    format = serializers.ChoiceField(
        choices=Application.FORMAT_CHOISES,
        label=Application._meta.get_field("format").verbose_name,
    )
    first_name = serializers.CharField(
        max_length=Application._meta.get_field("first_name").max_length,
        label=Application._meta.get_field("first_name").verbose_name,
    )
    last_name = serializers.CharField(
        max_length=Application._meta.get_field("last_name").max_length,
        label=Application._meta.get_field("last_name").verbose_name,
    )
    specializations = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(), many=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
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

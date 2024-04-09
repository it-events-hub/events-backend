from django.utils.functional import SimpleLazyObject

from users.models import User

APPLICATION_ANONYMOUS_REQUIRED_FIELDS_ERROR: str = (
    "Если заявка подается от имени анонимного посетителя, в ней должны быть указаны "
    "имя, фамилия, емейл, телефон и род деятельности."
)
APPLICATION_FORMAT_ERROR: str = (
    "Формат участия в заявке не соответствует формату проведения мероприятия."
)
APPLICATION_EMAIL_ERROR: str = (
    "Этот адрес электронной почты принадлежит другому пользователю. Если это ваш адрес "
    "электронной почты, пожалуйста, авторизуйтесь перед подачей заявки."
)
APPLICATION_PHONE_ERROR: str = (
    "Этот номер телефона принадлежит другому пользователю. "
    "Если это ваш номер телефона, пожалуйста, авторизуйтесь перед подачей заявки."
)
APPLICATION_TELEGRAM_ERROR: str = (
    "Этот Telegram ID принадлежит другому пользователю. Если это ваш Telegram ID, "
    "пожалуйста, авторизуйтесь перед подачей заявки."
)
APPLICATION_EVENT_EMAIL_UNIQUE_ERROR: str = (
    "Заявка на данное мероприятие от пользователя с таким адресом электронной почты "
    "уже существует."
)
APPLICATION_EVENT_PHONE_UNIQUE_ERROR: str = (
    "Заявка на данное мероприятие от пользователя с таким номером телефона уже "
    "существует."
)
APPLICATION_EVENT_TELEGRAM_UNIQUE_ERROR: str = (
    "Заявка на данное мероприятие от пользователя с таким Telegram ID уже существует."
)
NOTIFICATION_SETTINGS_APPLICATION_OF_USER_ERROR: str = (
    "Если заявка принадлежит зарегистрированному пользователю, настройки уведомлений "
    "должны быть привязаны к этому пользователю, а не к его отдельным заявкам."
)
APPLICATION_EVENT_STARTTIME_ERROR: str = (
    "Подача заявки на участие в мероприятии, которое уже началось, не допускается."
)
APPLICATION_ACTIVITY_ANONYMOUS_ERROR: str = "Укажите компанию, должность и опыт."
APPLICATION_ACTIVITY_AUTHORIZED_ERROR: str = (
    "Укажите компанию, должность и опыт в заявке или в своем Личном кабинете перед "
    "подачей заявки."
)
APPLICATION_FORMAT_REQUIRED_ERROR: str = (
    "Если мероприятие имеет гибридный формат, в заявке обязательно должен быть указан "
    "желаемый формат участия."
)
APPLICATION_SPECIALIZATIONS_REQUIRED_ERROR: str = (
    "Укажите направления в заявке или в своем Личном кабинете перед подачей заявки."
)
APPLICATION_EVENT_CLOSED_ERROR: str = "Регистрация на мероприятие закрыта."
APPLICATION_EVENT_OFFLINE_CLOSED_ERROR: str = (
    "Регистрация на мероприятие в офлайн-формате закрыта, но принимаются заявки "
    "на участие в мероприятии в онлайн-формате."
)
APPLICATION_EVENT_ONLINE_CLOSED_ERROR: str = (
    "Регистрация на мероприятие в онлайн-формате закрыта, но принимаются заявки "
    "на участие в мероприятии в офлайн-формате."
)
APPLICATION_USER_ALREADY_REGISTERED_ERROR: str = (
    "Данный пользователь уже зарегистрирован на данное мероприятие."
)


def check_another_user_email(
    user: User | SimpleLazyObject | None, email: str
) -> str | None:
    """Checks that the email does not belong to another user."""
    if user and User.objects.exclude(pk=user.pk).filter(email=email).exists():
        return APPLICATION_EMAIL_ERROR
    if not user and User.objects.filter(email=email).exists():
        return APPLICATION_EMAIL_ERROR
    return None


def check_another_user_phone(
    user: User | SimpleLazyObject | None, phone: str
) -> str | None:
    """Checks that the phone does not belong to another user."""
    if user and User.objects.exclude(pk=user.pk).filter(phone=phone).exists():
        return APPLICATION_PHONE_ERROR
    if not user and User.objects.filter(phone=phone).exists():
        return APPLICATION_PHONE_ERROR
    return None


def check_another_user_telegram(
    user: User | SimpleLazyObject | None, telegram: str
) -> str | None:
    """Checks that the telegram does not belong to another user."""
    if (
        user
        and telegram
        and User.objects.exclude(pk=user.pk).filter(telegram=telegram).exists()
    ):
        return APPLICATION_TELEGRAM_ERROR
    if not user and telegram and User.objects.filter(telegram=telegram).exists():
        return APPLICATION_TELEGRAM_ERROR
    return None

from datetime import date

from dateutil.relativedelta import relativedelta
from django.utils import timezone

MAX_EXPERIENCE_YEARS: int = 100
MAX_USER_AGE: int = 110
MIN_USER_AGE: int = 16
BIRTH_DATE_TOO_OLD_ERROR_MESSAGE: str = (
    "Указана неверная дата рождения, "
    f"пользователю должно быть не более {MAX_USER_AGE} лет."
)
BIRTH_DATE_TOO_YOUNG_ERROR_MESSAGE: str = (
    "Указана неверная дата рождения, "
    f"пользователю должно быть не менее {MIN_USER_AGE} лет."
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


def check_birth_date(birth_date: date) -> str | None:
    """Checks birth date."""
    print(type(birth_date))
    now = timezone.now()
    if birth_date and birth_date + relativedelta(years=MIN_USER_AGE) > now.date():
        return BIRTH_DATE_TOO_YOUNG_ERROR_MESSAGE
    if birth_date and birth_date + relativedelta(years=MAX_USER_AGE) < now.date():
        return BIRTH_DATE_TOO_OLD_ERROR_MESSAGE
    return None

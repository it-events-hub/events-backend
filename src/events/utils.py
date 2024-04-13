EVENT_ENDTIME_ERROR: str = "Мероприятие не может окончиться раньше времени его начала."
EVENT_PART_STARTTIME_ERROR: str = (
    "Часть мероприятия не может начинаться раньше самого мероприятия."
)
EVENT_CITY_REQUIRED_ERROR: str = (
    "Поле 'Город' обязательно к заполнению, "
    "если формат мероприятия 'offline' или 'гибрид'."
)
EVENT_PLACE_REQUIRED_ERROR: str = (
    "Поле 'Место' обязательно к заполнению, "
    "если формат мероприятия 'offline' или 'гибрид'."
)
SPEAKER_CREATE_VALIDATION_ERROR: str = (
    "При создании нового спикера должны быть указаны его ФИО (или имя + фамилия), "
    "место работы и должность."
)
SPEAKER_PATCH_NO_NAME_ERROR: str = "Укажите имя спикера."
EVENT_PART_NO_NAME_ERROR: str = "Укажите название этой части мероприятия."
EVENT_PART_NO_START_TIME_ERROR: str = (
    "Укажите дату и время начала этой части мероприятия."
)

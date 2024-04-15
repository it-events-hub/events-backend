# API сайта для Афиши IT-мероприятий

![Static Badge](https://img.shields.io/badge/status-in_progress-yellow) 
![main workflow](https://github.com/it-events-hub/events-backend/actions/workflows/main.yaml/badge.svg)
![Static Badge](https://img.shields.io/badge/Python-FFD43B?logo=python&logoColor=blue) 
![Static Badge](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=green)
![Static Badge](https://img.shields.io/badge/JWT-000000?logo=JSON%20web%20tokens&logoColor=white)
![Static Badge](https://img.shields.io/badge/celery-%2337814A.svg?logo=celery&logoColor=white)
![Static Badge](https://img.shields.io/badge/Swagger-85EA2D?logo=Swagger&logoColor=white)
![Static Badge](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)
![Static Badge](https://img.shields.io/badge/Docker-2CA5E0?logo=docker&logoColor=white) 
![Static Badge](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white) 
![Static Badge](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
![code style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

 # Описание проекта

Сервис для регистрации представителей IT-сообщества на мероприятия, в котором можно 
создавать и редактировать мероприятия, находить и регистрироваться на мероприятия.
Фронтенд взаимодействует с бэкендом через API.

С помощью API осуществляются:
- регистрация и авторизация пользователя;
- управление пользователем данными своего личного кабинета;
- хранение информации о мероприятиях;
- создание, редактирование, активация и деактивация мероприятий админами;
- отправка авторизованными и неавторизованными посетителями заявок на участие в мероприятиях;
- отправка людям, которые оставляли заявки на участие в мероприятиях, уведомлений об успешной подаче заявки;
- отправка людям, которые оставляли заявки на участие в мероприятиях, напоминаний о мероприятиях,
на которые они заявлялись - за день, за час или за 15 минут до начала (способ и 
расписание напоминаний настраивает человек, подавший заявку).

# Команда backend разработки

- [Galina Volkova](https://github.com/earlinn)
- [Nikolai Petrishchev](https://github.com/nikpetrischev)
- [Maksim Ukolov](https://github.com/link75)

# Динамически генерируемая документация апи

Чтобы посмотреть динамическую документацию апи, нужно запустить приложение и
пройти по одной из этих ссылок:
- в формате Swagger - https://hackathon-funtech.sytes.net/api/v1/swagger/
- в формате Redoc - https://hackathon-funtech.sytes.net/api/v1/redoc/

# Запуск проекта на локальном компьютере (без Docker)

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:it-events-hub/events-backend.git
cd events-backend
```

Создать в папке events-backend/src/config файл с названием ".env" и следующим 
содержанием:

```
SECRET_KEY=key
DOCKER=no
MODE=dev
ALLOWED_HOSTS=localhost web testserver 127.0.0.1 0.0.0.0 [::1]
CSRF_TRUSTED_ORIGINS=http://localhost/*
```

Установить Poetry - https://python-poetry.org/docs/#installation

C помощью Poetry создать и активировать виртуальное окружение:

```
poetry shell

# деактивировать виртуальное окружение можно командой
exit
```

Установить зависимости из файла poetry.lock

```
poetry install
```

Перейти в папку src и выполнить миграции:

```
cd src
python3 manage.py migrate
```

Собрать папку со статикой:

```
python3 manage.py collectstatic --no-input
```

Создать суперпользователя с правами администратора:

```
python3 manage.py createsuperuser
```

Локально запустить проект:

```
python3 manage.py runserver
```

Выйти из проекта: Ctrl + C.

# Запуск проекта на локальном компьютере в Docker Compose

## Клонирование репозитория, создание контейнеров и первоначальная сборка

_Важно: при работе в Linux или через терминал WSL2 все команды docker и docker compose нужно выполнять от имени суперпользователя — начинайте их с sudo._

Склонировать репозиторий на свой компьютер и перейти в него:
```
git clone git@github.com:it-events-hub/events-backend.git
cd events-backend
```

Создать в папке infra/ файл .env с необходимыми переменными окружения.

Пример содержимого файла:
```
SECRET_KEY=key
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
MODE=dev
DOCKER=yes
ALLOWED_HOSTS=localhost web testserver
CSRF_TRUSTED_ORIGINS=http://localhost/*
```

Запустить сборку контейнеров с помощью docker compose: 
```
docker compose -f docker-compose.local.yml up -d --build
```

После этого будут созданы и запущены в фоновом режиме контейнеры db, backend и nginx.

Внутри контейнера backend создать админа-суперпользователя для входа в Админку:
```
docker compose -f docker-compose.local.yml exec -it backend python manage.py createsuperuser
```

После этого Админка должна стать доступна по адресу: http://localhost/admin/
API Root будет доступен по адресу: http://localhost/api/

## Остановка и повторный запуск контейнеров

Для остановки работы приложения можно набрать в терминале команду Ctrl+C или открыть
второй терминал и выполнить команду:
```
docker compose stop 
```

Снова запустить контейнеры без их пересборки можно командой:
```
docker compose start 
```

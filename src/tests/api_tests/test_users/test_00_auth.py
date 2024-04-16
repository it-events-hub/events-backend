from http import HTTPStatus

import pytest

from users.models import User


@pytest.mark.django_db(transaction=True)
class Test00Auth:
    URL_CREATE_USER = "/api/v1/users/"
    URL_VERIFY_USER = "/api/v1/auth/jwt/verify/"

    def test_00_create_empty_user(self, client):
        response = client.post(self.URL_CREATE_USER)

        assert (response.status_code != HTTPStatus.NOT_FOUND,
            f"Эндпойнт {self.URL_CREATE_USER} не найден. Проверьте роутер.")

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f"POST-запрос на {self.URL_CREATE_USER} без необходимых данных "
            "должен вернуть ответ со статусом 400."
        )

        response_json = response.json()

        empty_fields = [
            "email",
            "password",
            "phone",
            "first_name",
            "last_name",
        ]
        errors_list: list = [error["attr"] for error in response_json["errors"]]
        for field in empty_fields:
            assert field in errors_list, (
                f"Если в POST-запросе к {self.URL_CREATE_USER} "
                "не переданы все необходимые поля, "
                "то они должны возвращаться в списке ошибок."
            )

    def test_00_invalid_data(self, client_with_wrong_email_and_phone):
        users_count = User.objects.count()
        response = client_with_wrong_email_and_phone.post(self.URL_CREATE_USER)

        assert (response.status_code != HTTPStatus.NOT_FOUND,
                f"Эндпойнт {self.URL_CREATE_USER} не найден, проверьте роутер.")

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f"Эндпойнт {self.URL_CREATE_USER} должен вернуть 400, "
            "если ему предоставлены некорректные данные."
        )

        assert users_count == User.objects.count(), (
            f"POST-запрос к {self.URL_CREATE_USER} с некорректными данными "
            "не должен создавать нового пользователя."
        )

        response_json = response.json()

        invalid_fields = ["email", "phone"]
        errors_list: list = [error["attr"] for error in response_json["errors"]]
        for field in invalid_fields:
            assert field in errors_list, (
                f"Если в POST-запросе к {self.URL_CREATE_USER} "
                "не переданы все необходимые поля, "
                "то они должны возвращаться в списке ошибок."
            )

    def test_00_verify_unauthorized_user(self, user_client_no_auth):
        response = user_client_no_auth.post(self.URL_VERIFY_USER)

        assert (response.status_code != HTTPStatus.NOT_FOUND,
            f"Эндпойнт {self.URL_CREATE_USER} не найден. Проверьте роутер.")

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f"Если POST-запрос к эндпойнту {self.URL_VERIFY_USER} "
            "не содержит токена, статус ответа должен быть 400."
        )

        response = user_client_no_auth.post(
            self.URL_VERIFY_USER,
            {"token": "Bearer wrong_token"},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f"Если POST-запрос к эндпйонту {self.URL_VERIFY_USER} "
            "содержит неверный токен, статус ответа должен быть 401."
        )

    def test_00_create_user_with_not_unique_fields(self, user_client):
        response = user_client.post(self.URL_CREATE_USER)

        assert (response.status_code != HTTPStatus.NOT_FOUND,
            f"Эндпойнт {self.URL_CREATE_USER} не найден, проверьте роутер.")

        users_count = User.objects.count()

        response = user_client.post(self.URL_CREATE_USER)
        response_json = response.json()

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            "При попытке создать пользователя с повторяющимися уникальными полями"
            " ответ должен возвращаться со статусом 400."
        )

        unique_fields = ["email", "phone"]
        errors_list: list = [error["attr"] for error in response_json["errors"]]
        for field in unique_fields:
            assert field in errors_list, (
                f"Если POST-запроос к {self.URL_CREATE_USER} "
                "содержит повтор уникальных полей, "
                "то их перечень должен быть в сообщении об ошибке."
            )

        assert User.objects.count() == users_count, (
            "Попытка создать пользователя с повторяющимися уникальными полями "
            "не должна приводить к сохранению пользователя в БД."
        )

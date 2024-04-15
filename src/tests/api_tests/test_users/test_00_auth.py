from http import HTTPStatus

import pytest


@pytest.mark.django_db(transaction=True)
class Test00Auth:

    # TODO: Add constants
    URL_CREATE_USER = "/api/v1/users/"

    def test_00_create_user(self, client):
        response = client.post(self.URL_CREATE_USER)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f"Эндпойнт {self.URL_CREATE_USER} не найден. Проверьте роутеры."
        )

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
        breakpoint()
        for field in empty_fields:
            assert field in errors_list, (
                f"Если в POST-запросе к {self.URL_CREATE_USER} "
                "не переданы все необходимые поля, "
                "то они должны возвращаться в списке ошибок."
            )

    def test_00_invalid_data(self, client):
        ...

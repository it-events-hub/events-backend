from http import HTTPStatus

import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from users.utils import MAX_USER_AGE, MIN_USER_AGE


@pytest.mark.django_db
class Test01UsersMe:
    URL_USERS_ME = "/api/v1/users/me/"

    def test_01_get_me_unauthorized(self, user_client_no_auth):
        response = user_client_no_auth.get(self.URL_USERS_ME)

        assert (
            response.status_code != HTTPStatus.NOT_FOUND
        ), f"Эндпойнт {self.URL_USERS_ME} не найден. Проверьте роутер."

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f"При GET-запросе к {self.URL_USERS_ME} неавторизованного "
            "пользователя статус ответа должен быть 401"
        )

    def test_01_patch_me_unauthorized(self, user_client_no_auth):
        response = user_client_no_auth.patch(self.URL_USERS_ME)

        assert (
            response.status_code != HTTPStatus.NOT_FOUND
        ), f"Эндпойнт {self.URL_USERS_ME} не найден. Проверьте роутер."

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f"При PATCH-запросе к {self.URL_USERS_ME} неавторизованного "
            "пользователя статус ответа должен быть 401"
        )

    def test_01_patch_me_wrong_regex_fields(
        self,
        user,
        user_client,
    ):
        if user:
            response = user_client.patch(
                self.URL_USERS_ME,
                data={
                    "telegram": "wrong_telegram",
                    "phone": "wrong_phone",
                },
            )

            assert (
                response.status_code != HTTPStatus.NOT_FOUND
            ), f"Эндпойнт {self.URL_USERS_ME} не найден. Проверьте роутер."

            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"PATCH-запрос на {self.URL_USERS_ME} с неправильными "
                "данными должен вернуть ответ со статусом 400."
            )

            response_json = response.json()

            wrong_fields = ["telegram", "phone"]
            errors_list: list = [error["attr"] for error in response_json["errors"]]
            for field in wrong_fields:
                assert field in errors_list, (
                    f"Если в PATCH-запросе к {self.URL_USERS_ME} "
                    'переданы поля "telegram" и "phone", '
                    "не соответствующие их регулярным выражениям, "
                    "то они должны возвращаться в списке ошибок."
                )

        else:
            raise AssertionError(
                f"Проверьте, что PATCH-запрос к {self.URL_USERS_ME} "
                "не приводит к удалению пользователя."
            )

    def test_00_patch_me_wrong_fields(self, user, user_client):
        if user:
            response = user_client.patch(
                self.URL_USERS_ME,
                data={
                    "email": "wrong_email",
                    "experience_years": -1,
                },
            )

            assert (
                response.status_code != HTTPStatus.NOT_FOUND
            ), f"Эндпойнт {self.URL_USERS_ME} не найден. Проверьте роутер."

            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"PATCH-запрос на {self.URL_USERS_ME} с неправильными "
                "данными должен вернуть ответ со статусом 400."
            )

            response_json = response.json()

            wrong_fields = ["email", "experience_years"]
            errors_list: list = [error["attr"] for error in response_json["errors"]]
            for field in wrong_fields:
                assert field in errors_list, (
                    f"Если в PATCH-запросе к {self.URL_USERS_ME} "
                    "переданы поля с недопустимыми значениями, "
                    "то они должны возвращаться в списке ошибок."
                )

        else:
            raise AssertionError(
                f"Проверьте, что PATCH-запрос к {self.URL_USERS_ME} "
                "не приводит к удалению пользователя."
            )

    def test_00_patch_me_birth_date(self, user, user_client):
        if user:
            response = user_client.patch(
                self.URL_USERS_ME,
                data={"birth_date": timezone.now().date()},
            )

            assert (
                response.status_code != HTTPStatus.NOT_FOUND
            ), f"Эндпойнт {self.URL_USERS_ME} не найден. Проверьте роутер."

            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"PATCH-запрос на {self.URL_USERS_ME} с возрастом меньше "
                f"{MIN_USER_AGE} лет должен вернуть ответ со статусом 400."
            )

            response_json = response.json()

            assert "birth_date" in response_json["errors"][0]["attr"], (
                f"Если в PATCH-запросе к {self.URL_USERS_ME} "
                "переданы поля с недопустимыми значениями, "
                "то они должны возвращаться в списке ошибок."
            )

            response = user_client.patch(
                self.URL_USERS_ME,
                data={
                    "birth_date": (
                        timezone.now() - relativedelta(years=(MAX_USER_AGE + 1))
                    ).date(),
                },
            )

            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"PATCH-запрос на {self.URL_USERS_ME} с возрастом больше "
                f"{MAX_USER_AGE} лет должен вернуть ответ со статусом 400."
            )

            response_json = response.json()

            assert "birth_date" in response_json["errors"][0]["attr"], (
                f"Если в PATCH-запросе к {self.URL_USERS_ME} "
                "переданы поля с недопустимыми значениями, "
                "то они должны возвращаться в списке ошибок."
            )

        else:
            raise AssertionError(
                f"Проверьте, что PATCH-запрос к {self.URL_USERS_ME} "
                "не приводит к удалению пользователя."
            )

    def test_01_patch_me_wrong_specs(self, user, user_client):
        if user:
            response = user_client.patch(
                self.URL_USERS_ME,
                data={"specializations": [-1]},
            )

            assert (
                response.status_code != HTTPStatus.NOT_FOUND
            ), f"Эндпойнт {self.URL_USERS_ME} не найден. Проверьте роутер."

            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"PATCH-запрос на {self.URL_USERS_ME} с ID несуществующей "
                "специализации должен вернуть ответ со статусом 400."
            )

            response_json = response.json()

            assert "specializations" in response_json["errors"][0]["attr"], (
                f"Если в PATCH-запросе к {self.URL_USERS_ME} "
                "переданы поля с недопустимыми значениями, "
                "то они должны возвращаться в списке ошибок."
            )

        else:
            raise AssertionError(
                f"Проверьте, что PATCH-запрос к {self.URL_USERS_ME} "
                "не приводит к удалению пользователя."
            )

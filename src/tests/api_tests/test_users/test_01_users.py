import re

import pytest


@pytest.mark.django_db
def test_user(user_factory):
    user = user_factory.create()
    assert re.fullmatch(r"^(\+7|7|8)\d{10}$", user.phone)

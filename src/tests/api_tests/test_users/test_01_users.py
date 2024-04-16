import re

import pytest

from users.utils import PHONE_NUMBER_REGEX


@pytest.mark.django_db
def test_user(user_factory):
    user = user_factory.create()
    assert re.fullmatch(PHONE_NUMBER_REGEX, user.phone) is not None

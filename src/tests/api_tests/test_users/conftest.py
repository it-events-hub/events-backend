from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

import pytest

from tests.api_tests import factories


@pytest.fixture
def user():
    user = factories.UserFactory()
    user.is_superuser = False
    user.is_staff = False
    return user


@pytest.fixture
def token_user(user):
    token = AccessToken.for_user(user)
    return {
        "access": str(token),
    }


@pytest.fixture
def user_client(token_user):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token_user['access']}",
    )
    return client


@pytest.fixture
def user_client_no_auth():
    return APIClient()


@pytest.fixture
def user_with_wrong_email_and_phone():
    user_with_wrong_email_and_phone = factories.UserWithWrongEmailAndPhoneFactory()
    return user_with_wrong_email_and_phone


@pytest.fixture
def client_with_wrong_email_and_phone(user_with_wrong_email_and_phone):
    return APIClient()

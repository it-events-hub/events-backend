from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

import pytest

from tests.api_tests import factories


@pytest.fixture
def user_superuser():
    superuser = factories.UserFactory()
    superuser.is_superuser = True
    superuser.is_staff = True
    return superuser


@pytest.fixture
def token_superuser(superuser):
    token = AccessToken.for_user(superuser)
    return {
        "access": str(token),
    }


@pytest.fixture
def superuser_client(token_superuser):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token_superuser['access']}",
    )
    return client


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


@pytest.fixture
def user_with_wrong_regex():
    user_with_wrong_regex = factories.UserWithWrongRegexFactory()
    return user_with_wrong_regex


@pytest.fixture
def token_with_wrong_regex(user_with_wrong_regex):
    token = AccessToken.for_user(user_with_wrong_regex)
    return {
        "access": str(token)
    }


@pytest.fixture
def client_with_wrong_regex(token_with_wrong_regex):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token_with_wrong_regex['access']}",
    )
    return client

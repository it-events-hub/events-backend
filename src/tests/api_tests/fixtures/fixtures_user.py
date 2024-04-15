import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken


@pytest.fixture
def user_superuser(user_factory):
    user = user_factory.build()
    user.is_superuser = True
    user.is_staff = True
    return user


@pytest.fixture
def user(user_factory):
    user = user_factory.build()
    user.is_superuser = False
    user.is_staff = False
    return user


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

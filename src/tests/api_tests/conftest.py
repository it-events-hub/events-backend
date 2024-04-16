from pytest_factoryboy import register

from tests.api_tests.factories import EventFactory, UserFactory

register(UserFactory)
register(EventFactory)

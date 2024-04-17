from pytest_factoryboy import register

from tests.api_tests.factories import (
    CityFactory,
    EventFactory,
    EventPartFactory,
    EventTypeFactory,
    SpeakerFactory,
    SpecializationFactory,
    UserFactory,
)

register(UserFactory)
register(EventFactory)
register(EventPartFactory)
register(EventTypeFactory)
register(SpeakerFactory)
register(SpecializationFactory)
register(CityFactory)

import factory
from faker import Faker
from faker.providers import DynamicProvider, profile

from events.models import City, Event, EventPart, EventType, Speaker
from users.models import Specialization, User

fake = Faker("ru_RU")

activity_dynamic_provider = DynamicProvider(
    provider_name="activities",
    elements=["ACTIVITY_WORK", "ACTIVITY_STUDY", "ACTIVITY_SEEK"],
)

fake.add_provider(profile)
fake.add_provider(activity_dynamic_provider)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = fake.unique.email()
    first_name = fake.first_name()
    last_name = fake.last_name()
    password = fake.password()
    phone = "8" + fake.numerify("##########")
    activity = fake.activities()

    birth_date = fake.profile()["birthdate"]
    experience_years = fake.numerify("%")
    telegram = "@" + fake.user_name()


class UserWithWrongEmailAndPhoneFactory(UserFactory):
    email = fake.unique.user_name()
    phone = fake.lexify("???????????")


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City

    name = "Москва"
    slug = "moscow"


class SpecializationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Specialization

    name = "бэкенд"
    slug = "backend"


class EventTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventType

    name = "конференция"
    slug = "conference"


class SpeakerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Speaker

    name = fake.unique.name()
    company = "Яндекс"
    position = "главный разработчик"
    description = fake.text()


class EventPartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventPart

    speaker = factory.SubFactory(SpeakerFactory)
    name = fake.unique.name()
    description = fake.text()
    created = "2024-04-03 11:39:06+03:00"
    start_time = fake.date_time()


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    name = fake.unique.name()
    description = fake.text()
    event_type = factory.SubFactory(EventTypeFactory)
    specializations = factory.SubFactory(SpecializationFactory)
    format = Event.FORMAT_ONLINE
    start_time = fake.date_time()
    event_parts = factory.SubFactory(EventPartFactory)

import factory
from faker import Faker
from faker.providers import DynamicProvider, profile

from events.models import Event
from users.models import User

fake = Faker("ru_RU")
fake.add_provider(profile)

activity_dynamic_provider = DynamicProvider(
    provider_name="activities",
    elements=["ACTIVITY_WORK", "ACTIVITY_STUDY", "ACTIVITY_SEEK"],
)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = fake.unique.email()
    first_name = fake.first_name()
    last_name = fake.last_name()
    phone = fake.phone_number()
    birth_date = fake.profile()["birthdate"]


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    name = fake.unique.name()

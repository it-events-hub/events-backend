import factory
from faker import Faker
from faker.providers import DynamicProvider, profile

from events.models import Event
from users.models import User

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


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    name = fake.unique.name()

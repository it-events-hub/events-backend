import os
import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from config import settings
from events.models import (
    City,
    EventType,
    Event,
    Speaker,
    EventPart,
)
from users.models import Specialization

DATA_DIR = os.path.join(settings.BASE_DIR, "data")


# Begin readers list
@transaction.atomic
def read_cities() -> None:
    """Reading from csv into City table."""
    with open(os.path.join(DATA_DIR, "cities.csv"), "r", encoding="utf-8") as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            city: City = City(
                name=row["name"],
                slug=row["slug"],
            )
            city.save()


@transaction.atomic
def read_event_types() -> None:
    """Reading from csv into EventType table."""
    with open(os.path.join(DATA_DIR, "event_types.csv"), "r", encoding="utf-8") as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            event_type: EventType = EventType(
                name=row["name"],
                slug=row["slug"],
            )
            event_type.save()


@transaction.atomic
def read_specializations():
    """Reading from csv into Specialization table."""
    with open(
            os.path.join(DATA_DIR, "specializations.csv"),
            "r",
            encoding="utf-8",
    ) as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            specialization: Specialization = Specialization(
                name=row["name"],
                slug=row["slug"],
            )
            specialization.save()


@transaction.atomic
def read_events():
    """Reading from csv into Event table."""
    with open(os.path.join(DATA_DIR, "events.csv"), "r", encoding="utf-8") as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            event: Event = Event()
            # for field in event._meta.get_fields():
            #     event.field = row[field.name]
            # for key in row.keys():
            #     field = event._meta.get_field(key)
            #     event.field = row[key]
            # TODO: Don't be fancy, do explicit fields
            event.save()


@transaction.atomic
def read_speakers():
    """Reading from csv into Speaker table."""
    ...


@transaction.atomic
def read_event_parts():
    """Reading from csv into EventPart table."""
    ...
# End readers list


class Command(BaseCommand):
    def handle(self, *args, **options):
        ...

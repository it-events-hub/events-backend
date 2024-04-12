import os
import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from api.loggers import logger
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
    City.objects.all().delete()
    with open(os.path.join(DATA_DIR, "City.csv"), "r", encoding="utf-8") as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            city: City = City(
                id=row["id"],
                name=row["name"],
                slug=row["slug"],
            )
            city.save()


@transaction.atomic
def read_event_types() -> None:
    """Reading from csv into EventType table."""
    EventType.objects.all().delete()
    with open(os.path.join(DATA_DIR, "EventType.csv"), "r", encoding="utf-8") as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            event_type: EventType = EventType(
                id=row["id"],
                name=row["name"],
                slug=row["slug"],
            )
            event_type.save()


@transaction.atomic
def read_specializations():
    """Reading from csv into Specialization table."""
    Specialization.objects.all().delete()
    with open(
            os.path.join(DATA_DIR, "Specialization.csv"),
            "r",
            encoding="utf-8",
    ) as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            specialization: Specialization = Specialization(
                id=row["id"],
                name=row["name"],
                slug=row["slug"],
            )
            specialization.save()


@transaction.atomic
def read_events():
    """Reading from csv into Event table."""
    Event.objects.all().delete()
    with open(os.path.join(DATA_DIR, "Events.csv"), "r", encoding="utf-8") as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            event: Event = Event(
                id=row["id"],
                name=row["name"],
                organization=row["organization"],
                description=row["description"],
                is_deleted=(row["is_deleted"].lower() == "true"),
                status=row["status"],
                format=row["format"],
                # created=row["created"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                cost=row["cost"],
                city=City.objects.filter(pk=row["city"]).first(),
                place=row["place"],
                event_type=EventType.objects.get(pk=row["event_type"]),
                specializations=Specialization.objects.get(pk=row["specialization"]),
                participant_offline_limit=row["participant_offline_limit"],
                participant_online_limit=row["participant_online_limit"],
                registration_deadline=row["registration_deadline"],
                livestream_link=row["livestream_link"],
                additional_materials_link=row["additional_materials_link"],
                image=row["image"],
                is_featured=(row["is_featured"].lower() == "true"),
                is_featured_on_yandex_afisha=(
                        row["is_featured_on_yandex_afisha"].lower() == "true"
                ),
            )
            event.save()


@transaction.atomic
def read_speakers():
    """Reading from csv into Speaker table."""
    Speaker.objects.all().delete()
    with open(os.path.join(DATA_DIR, "Speakers.csv"), "r", encoding="utf-8") as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            speaker: Speaker = Speaker(
                id=row["id"],
                name=row["name"],
                company=row["company"],
                position=row["position"],
                description=row["description"],
                photo=row["photo"],
            )
            speaker.save()


@transaction.atomic
def read_event_parts():
    """Reading from csv into EventPart table."""
    EventPart.objects.all().delete()
    with open(os.path.join(DATA_DIR, "EventPart.csv"), "r", encoding="utf-8") as f:
        reader: csv.DictReader = csv.DictReader(f)
        for row in reader:
            event_part: EventPart = EventPart(
                id=row["id"],
                event=Event.objects.get(pk=row["event"]),
                name=row["name"],
                description=row["description"],
                speaker=Speaker.objects.filter(pk=row["speaker"]).first(),
                start_time=row["start_time"],
                presentation_type=row["presentation_type"],
            )
            event_part.save()
# End readers list


class Command(BaseCommand):
    def handle(self, *args, **options):
        for func in (
            read_cities,
            read_event_types,
            read_specializations,
            read_events,
            read_speakers,
            read_event_parts,
        ):
            logger.info(f"Begin {func.__name__}...")
            try:
                func()
                logger.info(f"{func.__name__} successfully executed.")
            except Exception as e:
                logger.error(f"{func.__name__} failed.\n{e}")
                break

        logger.info("Loading data from csv is completed.")

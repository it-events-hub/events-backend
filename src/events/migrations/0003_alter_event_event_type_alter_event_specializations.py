# Generated by Django 5.0.3 on 2024-04-06 10:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_eventpart_description"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="event_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to="events.eventtype",
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="specializations",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to="users.specialization",
                verbose_name="Направление",
            ),
        ),
    ]

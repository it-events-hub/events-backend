from django.contrib import admin

from .models import Event, EventPart, EventType, Speaker


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    """Class to display types of events in admin panel."""

    list_display = ["pk", "name", "slug"]
    list_display_links = ["name"]
    search_fields = ["name", "slug"]
    ordering = ["pk"]


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    """Class to display speakers in admin panel."""

    list_display = ["pk", "name", "company", "position"]
    list_display_links = ["name"]
    search_fields = ["name", "company"]
    list_filter = ["position"]
    ordering = ["pk"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Class to display events in admin panel."""

    list_display = [
        "pk",
        "name",
        "event_type",
        "specializations",
        "is_deleted",
        "status",
        "format",
        "start_time",
        "cost",
    ]
    list_display_links = ["name"]
    search_fields = ["name"]
    list_filter = [
        "is_deleted",
        "status",
        "format",
        "event_type",
        "specializations",
        "start_time",
        "cost",
    ]
    ordering = ["pk"]


@admin.register(EventPart)
class EventPartAdmin(admin.ModelAdmin):
    """Class to display events agenda items in admin panel."""

    list_display = [
        "pk",
        "name",
        "speaker",
        "presentation_type",
        "start_time",
        "event",
        "is_deleted",
    ]
    list_display_links = ["name"]
    search_fields = ["name", "event__name", "speaker__name"]
    list_filter = ["is_deleted", "start_time", "presentation_type"]
    ordering = ["pk"]

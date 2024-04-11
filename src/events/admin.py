from django.contrib import admin

from .models import City, Event, EventPart, EventType, Speaker


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    """Class to display types of events in admin panel."""

    list_display = ["pk", "name", "slug"]
    list_display_links = ["name"]
    search_fields = ["name", "slug"]
    ordering = ["pk"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Class to display cities of events in admin panel."""

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
        "participant_offline_limit",
        "participant_online_limit",
        "start_time",
        "submitted_applications",
    ]
    list_display_links = ["name"]
    search_fields = ["name"]
    list_filter = [
        "is_deleted",
        "status",
        "format",
        "event_type",
        "specializations",
        "city",
        "start_time",
        "cost",
    ]
    ordering = ["pk"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "city", "event_type", "specializations"
        ).prefetch_related("applications")

    @admin.display(description="Заявки")
    def submitted_applications(self, obj):
        """Shows the number of applications submitted to participate in the event."""
        return obj.applications.count()


@admin.register(EventPart)
class EventPartAdmin(admin.ModelAdmin):
    """Class to display events agenda items in admin panel."""

    list_display = [
        "pk",
        "event",
        "name",
        "speaker",
        "presentation_type",
        "start_time",
    ]
    list_display_links = ["name"]
    search_fields = ["name", "event__name", "speaker__name"]
    list_filter = ["start_time", "presentation_type"]
    ordering = ["pk"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("event", "speaker")

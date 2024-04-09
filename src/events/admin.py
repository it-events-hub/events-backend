from django.contrib import admin

from .models import City, Event, EventPart, EventType, Speaker


# TODO: создает дубли sql-запросов на странице отдельного ивента, если добавить
# поле speaker в exclude, то дубликатов становится поменьше, но совсем они не исчезают,
# погуглить django admin inline duplicated queries
class EventPartsInline(admin.TabularInline):
    """Inline class to display event parts on event details page in Admin panel."""

    model = EventPart
    exclude = ["created"]
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("speaker")


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
        "city",
        "participant_offline_limit",
        "participant_online_limit",
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
        "city",
        "start_time",
        "cost",
    ]
    ordering = ["pk"]
    inlines = [EventPartsInline]  # TODO: если отключить, дублей sql-запросов не будет

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("city", "event_type", "specializations")


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
    ]
    list_display_links = ["name"]
    search_fields = ["name", "event__name", "speaker__name"]
    list_filter = ["start_time", "presentation_type"]
    ordering = ["pk"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("event", "speaker")

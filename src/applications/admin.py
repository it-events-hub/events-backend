from django.contrib import admin

from .models import Application, Notification, NotificationSettings, Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    """Class to display sources of information about events in admin panel."""

    list_display = ["pk", "name", "slug"]
    list_display_links = ["name"]
    search_fields = ["name", "slug"]
    ordering = ["pk"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Class to display applications for participation in events in admin panel."""

    list_display = ["pk", "event", "user", "first_name", "last_name", "status"]
    list_display_links = ["event"]
    search_fields = [
        "event__name",
        "user__email",
        "user__phone",
        "user__first_name",
        "user__last_name",
        "first_name",
        "last_name",
    ]
    list_filter = ["status", "source"]
    ordering = ["pk"]


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    """Class to display event notification settings in admin panel."""

    list_display = [
        "pk",
        "user",
        "application",
        "email_notifications",
        "sms_notifications",
        "telegram_notifications",
        "phone_call_notifications",
    ]
    list_display_links = ["user", "application"]
    list_filter = [
        "email_notifications",
        "sms_notifications",
        "telegram_notifications",
        "phone_call_notifications",
    ]
    ordering = ["pk"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Class to display notification celery task_id related to a specific application
    in admin panel.
    """

    list_display = ["pk", "task_id", "application"]
    list_display_links = ["task_id"]
    search_fields = ["task_id", "application__event__name", "application__user__email"]
    ordering = ["pk"]

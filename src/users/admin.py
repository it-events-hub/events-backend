from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Specialization, User


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    """Class to display IT directions in admin panel."""

    list_display = ["pk", "name", "slug"]
    list_display_links = ["name"]
    search_fields = ["name", "slug"]
    ordering = ["pk"]


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Class to display users in admin panel."""

    list_display = [
        "pk",
        "email",
        "first_name",
        "last_name",
        "activity",
        "is_active",
        "is_superuser",
        "date_joined",
        "last_login",
    ]
    list_display_links = ["email"]
    search_fields = [
        "email",
        "phone",
        "telegram",
        "first_name",
        "last_name",
        "company",
        "position",
    ]
    list_filter = [
        "is_active",
        "is_superuser",
        "is_staff",
        "specializations",
        "activity",
        "experience_years",
        "date_joined",
        "last_login",
        "birth_date",
        "city",
    ]
    ordering = ["pk"]
    fieldsets = (
        (None, {"fields": ("email", "phone", "telegram", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "birth_date",
                    "city",
                    "activity",
                    "company",
                    "position",
                    "experience_years",
                    "specializations",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

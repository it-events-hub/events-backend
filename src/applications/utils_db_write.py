from .models import Application, NotificationSettings
from users.models import User


def create_notification_settings(
    user_pk: int | None = None, application_pk: int | None = None
) -> None:
    """Creates notification settings object linked to the user or to the application."""
    user = User.objects.get(pk=user_pk) if user_pk else None
    application = Application.objects.get(pk=application_pk) if application_pk else None
    NotificationSettings.objects.create(user=user, application=application)

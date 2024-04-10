from .models import Application, NotificationSettings
from api.loggers import logger
from users.models import User


def create_notification_settings(
    user: User | None = None, application: Application | None = None
) -> None:
    """Creates notification settings object linked to the user or to the application."""
    NotificationSettings.objects.create(user=user, application=application)
    logger.debug(
        f"Notification settings for user {user}, application {application} were added."
    )

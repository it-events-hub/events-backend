from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_email_after_submission_of_application(
    first_name: str, event: str, to_email: str, **kwargs
) -> None:
    """
    Sends an email about the successful submission of an application for participation
    in the event.
    """
    subject = "Заявка на участие в мероприятии успешно подана"
    message = render_to_string(
        "submit_application.html", {"first_name": first_name, "event": event}
    )
    send_mail(subject, message, from_email=None, recipient_list=[to_email])

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_email_after_submission_of_application(
    first_name: str, event_name: str, to_email: str, **kwargs
) -> None:
    """
    Sends an email about the successful submission of an application for participation
    in the event.
    """
    subject = "Заявка на участие в мероприятии успешно подана"
    message = render_to_string(
        "submit_application.html", {"first_name": first_name, "event": event_name}
    )
    send_mail(subject, message, from_email=None, recipient_list=[to_email])


@shared_task
def remind_participant_about_upcoming_event(
    first_name: str, event_name: str, date: str, time: str, to_email: str, **kwargs
) -> None:
    """
    Reminds the person who applied to participate in the event
    that the event will start soon.
    """
    subject = "Напоминание о предстоящем мероприятии"
    message = render_to_string(
        "remind_by_email.html",
        {"first_name": first_name, "event": event_name, "date": date, "time": time},
    )
    send_mail(subject, message, from_email=None, recipient_list=[to_email])

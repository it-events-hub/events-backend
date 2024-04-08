from django.core.mail import EmailMessage


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            to=[data["send_to"]],
        )
        email.send()

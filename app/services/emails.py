from django.core.mail import send_mail
from django.template.loader import render_to_string
from app.models import SentEmailsMessages


class EmailService:
    @staticmethod
    def send_email(
        recipient_emails,
        message: str,
        subject: str,
        sender: str,
    ):
        subject = subject
        message = message
        from_email = sender
        recipient_list = list(set(recipient_emails))

        for recipient in recipient_list:
            has_errors = False
            error_message = None
            if(len(recipient.split(",")) >= 2):
                recipient = recipient.split(",")
            else:
                recipient = [recipient]
            try:
                send_mail(
                    subject,
                    render_to_string('emails/vacanta.txt', context={"message": message}),
                    from_email,
                    recipient,
                )
            except Exception as e:
                print(f"Error sending email to: {recipient}. Original error caused by: {e}")
                has_errors = True
                error_message = e

            SentEmailsMessages.objects.create(
                sent_to_mail=str(recipient),
                sent_mail_subject=subject,
                sent_mail_body=message,
                has_errors=has_errors,
                error_message=error_message,
            )

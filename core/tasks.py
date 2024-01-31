from celery import shared_task

from app.services.emails import EmailService


@shared_task
def send_trainer_registration_email(
    email: str,
    username: str,
    password: str,
):
    print("Task received")
    EmailService.send_email(
        recipient_emails=[email],
        message=f"""
Salut,
Username: {username},
Parola: {password}
""",
            subject="Invitatie internal_lsc",
            sender="gabi.isaila@logiscool.com"
        )
    
@shared_task
def send_students_email(emails, subject, message):
    EmailService.send_email(
        recipient_emails=emails,
        message=message,
        subject=subject,
       sender="Logiscool Bucrești Romană <hello.romana@logiscool.com>",
    )

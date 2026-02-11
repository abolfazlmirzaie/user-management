from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_verification_email_task(email, code):
    send_mail(
        subject="email verification",
        message=f"your verification code is : {code}",
        from_email=None,
        recipient_list=[email],
    )

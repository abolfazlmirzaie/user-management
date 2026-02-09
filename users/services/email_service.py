from django.core.mail import send_mail




class EmailService:
    @staticmethod
    def send_verification_email(email, code):
        send_mail(
            subject="email verification",
            message=f"your verification code is : {code}",
            from_email=None,
            recipient_list=[email],
        )

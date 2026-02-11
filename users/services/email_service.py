from users.tasks import send_verification_email_task


class EmailService:
    @staticmethod
    def send_verification_email(email, code):
        send_verification_email_task.delay(email, code)

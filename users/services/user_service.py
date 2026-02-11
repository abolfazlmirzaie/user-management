from django.contrib.auth import authenticate, login, logout

from users.models import CustomUser as User

from .email_service import EmailService
from .otp_service import OTPService


class UserService:
    @staticmethod
    def can_verify_email(user):
        if not user.email:
            return False, "you do not have an email"
        if user.is_verified:
            return False, "you are already verified"
        return True, None

    @staticmethod
    def enable_two_factor(user):
        if not user.is_verified:
            return False, "your email is not verified"
        user.two_factor_enabled = True
        user.save()
        return True, None

    @staticmethod
    def login(username, password):
        user = authenticate(username=username, password=password)
        if not user:
            return False, "invalid username or password", None
        if not user.is_verified:
            return None, "you are logged in", user

        code = OTPService.generate_otp(user.email)
        EmailService.send_verification_email(user.email, code)

        return None, "otp sent", user

from django.contrib.auth import authenticate
from rest_framework.response import Response

from courses.models import Enrollment
from users.models import Instructor, InstructorApplication
from rest_framework.exceptions import ValidationError
from users.models import CustomUser as User
from django.db import transaction
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


class InstructorService:
    @staticmethod
    def submit_application(*, user, motivation):
        if Instructor.objects.filter(user=user).exists():
            raise ValidationError(
                {"detail": "you are already an instruct"},
            )

        if InstructorApplication.objects.filter(user=user, status="pending").exists():
            raise ValidationError(
                {"detail": "you already sent as application"},
            )

        with transaction.atomic():
            application = InstructorApplication.objects.create(
                user=user,
                motivation=motivation,
                status="pending",
            )
        return application


class EnrollmentService:
    @staticmethod
    def enroll(user, course):
        if Enrollment.objects.filter(user=user, course=course).exists():
            raise ValidationError("already enrolled")
        if course.is_premium:
            raise ValidationError("premium course")

        return Enrollment.objects.create(user=user, course=course)

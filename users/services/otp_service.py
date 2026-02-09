import random
from users.models import EmailOTP

class OTPService:
    @staticmethod
    def generate_otp(email):
        code = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(email=email, defaults={"code": code})
        return code

    @staticmethod
    def verify_otp(email, code):
        otp = EmailOTP.objects.get(email=email)

        try:
            otp = EmailOTP.objects.get(email=email)
        except EmailOTP.DoesNotExist:
            return False, "there is no code for this email"

        if otp.is_expired():
            return False, "the code is expired"

        if otp.code != code:
            return False, "the code is invalid"

        return True, None

    @staticmethod
    def delete_otp(email):
        otp = EmailOTP.objects.get(email=email).delete()

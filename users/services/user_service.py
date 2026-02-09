
class UserEmailService:
    @staticmethod
    def can_verify_email(user):
        if not user.email:
            return False, "you do not have an email"
        if user.is_verified:
            return False, "you are already verified"
        return True, None
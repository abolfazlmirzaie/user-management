import re

from django.core.exceptions import ValidationError


class PasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number")

        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("Password must contain at least one letter")

        if not re.search(r"[!@#%&*()_]", password):
            raise ValidationError(
                "Password must contain at least one special character"
            )

        return password

    def get_help_text(self):
        return ""

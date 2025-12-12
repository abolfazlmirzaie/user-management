from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, EmailOTP, OTPLogin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ("username", "email", "is_verified", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Status",
            {"fields": ("is_verified", "is_active", "is_staff", "is_superuser")},
        ),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    search_fields = ("email", "username")
    ordering = ("email",)


admin.site.register(EmailOTP)
admin.site.register(OTPLogin)

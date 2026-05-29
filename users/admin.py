from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, EmailOTP, OTPLogin, SubscriptionPlan, Ticket


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ("username", "is_verified", "is_staff", "is_active")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "full_name",
                    "email",
                    "profile_picture",
                    "password",
                )
            },
        ),
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


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration_days")
    search_fields = ("name",)
    ordering = ("price",)


admin.site.register(EmailOTP)


admin.site.register(OTPLogin)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("user", "is_replied")
    list_filter = ("is_replied", "user")

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (CustomUser, EmailOTP, OTPLogin, Subscription,
                     SubscriptionPlan)


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
                    "email",
                    "profile_picture",
                    "first_name",
                    "last_name",
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


admin.site.register(EmailOTP)
admin.site.register(OTPLogin)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration_days")
    search_fields = ("name",)
    ordering = ("price",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "active")
    list_filter = ("active", "plan")
    search_fields = ("user__username", "plan__name")
    ordering = ("-start_date",)
    # exclude = ("start_date", "end_date")

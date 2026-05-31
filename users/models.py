import datetime
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    full_name = models.CharField("full_name", max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        upload_to="profile_pictures", default="profile_pic/profile.png"
    )

    def __str__(self):
        return self.username


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    duration_days = models.IntegerField()

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.CASCADE, related_name="subscriptions"
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = timezone.now() + datetime.timedelta(
                days=self.plan.duration_days
            )
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user} - {self.plan.name}"


class EmailOTP(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + datetime.timedelta(minutes=5)


class OTPLogin(models.Model):
    email = models.EmailField(unique=True, blank=True, null=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + datetime.timedelta(minutes=5)


class Ticket(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="tickets"
    )
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_replied = models.BooleanField(default=False)
    replay_content = models.TextField(default="")

    def __str__(self):
        return self.user.username


class Instructor(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="instructors"
    )
    bio = models.TextField(default="")
    avatar = models.ImageField(upload_to="instructors/avatars/", blank=True, null=True)
    expertise = models.TextField(default="")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InstructorApplication(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    motivation = models.TextField(default="")
    status = models.CharField(
        choices=[
            ("pending", "pending"),
            ("approved", "approved"),
            ("rejected", "rejected"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="pending"),
                name="unique_pending_instructor_application",
            )
        ]

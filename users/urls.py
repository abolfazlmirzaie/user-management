from django.urls import path

from .views import (
    EditProfileView,
    EmailLoginView,
    EnableTwoFactorView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PlanListView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    VerifyCodeView,
    VerifyOTPEmailLoginView,
    VerifyOTPLoginView, VerifyUserEmailView,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user-register"),
    path("edit-profile/", EditProfileView.as_view(), name="edit_profile"),
    path(
        "enable-two-factor-login/",
        EnableTwoFactorView.as_view(),
        name="enable-two-factor-login",
    ),
    path(
        "verify-email/",
        VerifyUserEmailView.as_view(),
        name="verify-email",
    ),
    path("login/", UserLoginView.as_view(), name="login"),
    path("verify_login/", VerifyOTPLoginView.as_view(), name="verify_login"),
    path("plans/", PlanListView.as_view(), name="subscription_plan_list"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("otp-verify/", VerifyCodeView.as_view(), name="otp-verify"),
    path("email-login/", EmailLoginView.as_view(), name="email-login"),
    path(
        "otp-login-verify/", VerifyOTPEmailLoginView.as_view(), name="otp-login-verify"
    ),
    path(
        "password-reset-request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "reset-password/<uid>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]

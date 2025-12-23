from django.urls import path

from .views import (EditProfileView, EnableTwoFactorView, OTPLoginView,
                    OTPVerifyLoginView, PasswordResetConfirmView,
                    PasswordResetRequestView, UserLoginView, UserLogoutView,
                    UserRegisterView, VerifyCodeView, VerifyEmailView,
                    VerifyTwoFactorLogin)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("edit-profile/", EditProfileView.as_view(), name="edit_profile"),
    path(
        "enable-two-factor-login/",
        EnableTwoFactorView.as_view(),
        name="enable-two-factor-login",
    ),
    path(
        "verify-two-factor-login/",
        VerifyTwoFactorLogin.as_view(),
        name="verify-two-factor-login",
    ),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("email-verify/", VerifyEmailView.as_view(), name="email-verify"),
    path("otp-verify/", VerifyCodeView.as_view(), name="otp-verify"),
    path("otp-login/", OTPLoginView.as_view(), name="otp-login"),
    path("otp-login-verify/", OTPVerifyLoginView.as_view(), name="otp-login-verify"),
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

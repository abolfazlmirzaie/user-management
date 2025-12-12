from django.urls import path

from .views import (
    OTPLoginView,
    OTPVerifyLoginView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    VerifyCodeView,
    VerifyEmailView,
)


app_name = "users"
urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("email-verify/", VerifyEmailView.as_view(), name="email-verify"),
    path("otp-verify/", VerifyCodeView.as_view(), name="otp-verify"),
    path("otp-login/", OTPLoginView.as_view(), name="otp-login"),
    path("otp-login-verify/", OTPVerifyLoginView.as_view(), name="otp-login-verify"),
]

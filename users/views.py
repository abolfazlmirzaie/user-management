import random

from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.shortcuts import redirect
from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from .models import CustomUser, EmailOTP, OTPLogin
from .serializers import (
    OTPVerifyLoginSerializer,
    UserEmailLoginSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    VerifyEmailSerializer,
    EditUserProfileSerializer,
)


class UserRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response(
                {"message": "you are logged in"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        email = request.user.email
        if not email:
            return Response({"error": "you dont have an email"}, status=400)

        if request.user.is_verified:
            return Response("your email is already verified", status=status.HTTP_200_OK)

        code = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(email=email, defaults={"code": code})

        send_mail(
            subject="email verification",
            message=f"your verification code is : {code}",
            from_email=None,
            recipient_list=[email],
        )

        return redirect("users:otp-verify")


class VerifyCodeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]
        email = request.user.email

        try:
            otp = EmailOTP.objects.get(email=email)
        except EmailOTP.DoesNotExist:
            return Response("there is no code for this email", status=400)

        if otp.is_expired():
            otp.delete()
            return Response("code is expired", status=400)

        if otp.code != code:
            return Response("the giving code is incorrect", status=400)

        otp.delete()
        user = CustomUser.objects.get(email=email)
        user.is_verified = True
        user.save()
        return Response(
            "your email has been verified !", status=status.HTTP_200_OK
        ), redirect("/")




class EnableTwoFactorView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if request.user.is_verified:
            user = CustomUser.objects.get(email=request.user.email)
            user.two_factor_enabled = True
            user.save()
            return Response({"message": "your two factor login is now enable"}, status=status.HTTP_200_OK)
        return Response({"message": "you are not verified"}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if user.two_factor_enabled:
                code = str(random.randint(100000, 999999))
                request.session["email"] = user.email
                EmailOTP.objects.update_or_create(email=user.email, defaults={"code": code})
                send_mail(
                    subject="email verification",
                    message=f"your otp code is : {code}",
                    from_email=None,
                    recipient_list=[user.email])
                return Response({"message": "your code has been sent"}, status=status.HTTP_200_OK)
            login(request, user)
            return Response({"message": "you are logged in"}, status=status.HTTP_200_OK)

        return Response(
            {"message": "your username or password is incorrect"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            logout(request)
            return Response(
                {"message": "you are logged out"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "you are not logged in"}, status=status.HTTP_400_BAD_REQUEST
            )


class OTPLoginView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UserEmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"message": "the giving email is incorrect"}, status=400)

        if not user.is_verified:
            return Response("your email is al verified", status=status.HTTP_200_OK)

        code = random.randint(100000, 999999)
        request.session["email"] = email
        OTPLogin.objects.update_or_create(email=email, defaults={"code": code})

        send_mail(
            subject="email verification",
            message=f"your otp code is : {code}",
            from_email=None,
            recipient_list=[email],
        )
        return Response(
            {"message": "your code has beem sent"}, status=status.HTTP_200_OK
        )


class OTPVerifyLoginView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = OTPVerifyLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]


        # just for test API
        # you can get the EMAIL from session ----- email = request.session.get["email"]
        email = serializer.validated_data["email"]


        try:
            otp = OTPLogin.objects.get(email=email)
        except OTPLogin.DoesNotExist:
            return Response({"message": "there is no code for this email"}, status=400)

        if otp.is_expired():
            otp.delete()
            return Response({"message": "code is expired"}, status=400)

        if otp.code != code:
            return Response({"message": "the giving code is incorrect"}, status=400)

        otp.delete()
        user = CustomUser.objects.get(email=email)
        login(request, user)
        return Response({"message": "you are logged in"}, status=status.HTTP_200_OK)






class VerifyTwoFactorLogin(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPVerifyLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]


        # just for test API
        # you can get the EMAIL from session ----- email = request.session.get["email"]
        email = serializer.validated_data["email"]


        try:
            otp = EmailOTP.objects.get(email=email)
        except EmailOTP.DoesNotExist:
            return Response({"message": "there is no code for this email"}, status=400)

        if otp.is_expired():
            otp.delete()
            return Response({"message": "code is expired"}, status=400)

        if otp.code != code:
            return Response({"message": "the giving code is incorrect"}, status=400)

        otp.delete()
        user = CustomUser.objects.get(email=email)
        login(request, user)
        return Response({"message": "you are logged in"}, status=status.HTTP_200_OK)




class EditProfileView(RetrieveUpdateAPIView):
    serializer_class = EditUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user



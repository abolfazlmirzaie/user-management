import random

from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.shortcuts import redirect
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from .models import CustomUser
from .models import CustomUser as User
from .models import EmailOTP, OTPLogin, SubscriptionPlan
from .serializers import (EditUserProfileSerializer, OTPSerializer,
                          OTPVerifyLoginSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetRequestSerializer,
                          UserEmailLoginSerializer, UserLoginSerializer,
                          UserRegisterSerializer)
from .services.email_service import EmailService
from .services.otp_service import OTPService
from .services.user_service import UserService
from .throttles import LoginThrottle


class UserRegisterView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(
            {"message": "you are logged in"}, status=status.HTTP_201_CREATED
        )


class VerifyEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = [UserRateThrottle]

    def post(self, request, *args, **kwargs):
        email = request.user.email
        ok, msg = UserService.can_verify_email(email)
        if not ok:
            return Response({"message": msg}, status=status.HTTP_400_BAD_REQUEST)
        code = OTPService.generate_otp(email)
        EmailService.send_verification_email(email, code)

        return redirect("users:otp-verify")


class VerifyCodeView(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["otp"]
        email = request.user.email

        ok, msg = OTPService.verify_otp(email, code)
        if not ok:
            return Response({"message": msg}, status=status.HTTP_400_BAD_REQUEST)
        request.user.is_verified = True

        request.euser.save()
        return Response("your email has been verified !", status=status.HTTP_200_OK)


class EnableTwoFactorView(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        ok, msg = UserService.enable_two_factor(request.user)
        if not ok:
            return Response({"message": msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "two factory login enabled!"}, status=status.HTTP_200_OK
        )


class UserLoginView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if request.user.is_authenticated:
            return Response(
                {"message": "you are already logged in"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            ok, msg, user = UserService.login(user.username, request.data["password"])

            if ok:
                login(request, user)
                return Response({"message": msg}, status=status.HTTP_200_OK)
            if ok is None:
                request.session["pending_user_id"] = user.id
                return Response({"message": "otp sent"}, status=status.HTTP_200_OK)
        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPLoginView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.session.get("pending_user_id")
        if not user_id:
            return Response(
                {"message": "no pending login"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.get(id=user_id)
        code = serializer.validated_data["otp"]

        ok, msg = OTPService.verify_otp(user.email, code)
        if not ok:
            return Response({"message": msg}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        del request.session["pending_user_id"]

        return Response({"message": "you are logged in"}, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    throttle_classes = [LoginThrottle]

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
    throttle_classes = [LoginThrottle]

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
    throttle_classes = [UserRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = OTPVerifyLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]

        # just for test the API
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
    throttle_classes = [LoginThrottle]

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
    throttle_classes = [UserRateThrottle]
    serializer_class = EditUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "your reset link has been sent"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request, uid, token):
        serializer = PasswordResetConfirmSerializer(
            data={"new_password": request.data.get("new_password")},
            uid=uid,
            token=token,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"message": "your password has been changed"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# views.py


class PlanListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        data = [
            {
                "name": plan.name,
                "price": plan.price,
                "duration_days": plan.duration_days,
            }
            for plan in plans
        ]
        return Response(data)

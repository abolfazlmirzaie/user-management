from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser as User, InstructorApplication, PendingLogin
from .models import SubscriptionPlan, Ticket
from .serializers import (
    EditUserProfileSerializer,
    OTPSerializer,
    OTPVerifyLoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserEmailLoginSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    TicketSerializer,
    InstructorApplicationSerializer,
)
from .services.email_service import EmailService
from .services.otp_service import OTPService
from .services.user_service import UserService, InstructorService
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


class VerifyUserEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = [UserRateThrottle]

    def post(self, request, *args, **kwargs):
        email = request.user.email
        ok, msg = UserService.can_verify_email(email)
        if not ok:
            return Response({"message": msg}, status=status.HTTP_400_BAD_REQUEST)
        code = OTPService.generate_otp(email)
        EmailService.send_verification_email(email, code)

        return Response("your code has been sent", status=status.HTTP_200_OK)


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
        OTPService.delete_otp(email)
        request.user.save(update_fields=["is_verified"])
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
        if request.user.is_authenticated:
            return Response(
                {"message": "you are already logged in"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        ok, msg, user = UserService.login(user.username, request.data["password"])
        if ok:
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        if ok is None:
            PendingLogin.objects.filter(user=user).delete()
            pending_login = PendingLogin.objects.create(user=user)
            return Response(
                {
                    "message": "otp sent",
                    "pending_token": str(pending_login.token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": msg},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyOTPLoginView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):

        serializer = OTPVerifyLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pending_login = get_object_or_404(
            PendingLogin,
            token=serializer.validated_data["pending_token"],
        )

        user = pending_login.user
        otp = serializer.validated_data["otp"]

        ok, msg = OTPService.verify_otp(user.email, otp)

        if not ok:
            return Response(
                {"message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        OTPService.delete_otp(user.email)

        refresh = RefreshToken.for_user(user)

        pending_login.delete()

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class EmailLoginView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = UserEmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = get_object_or_404(User, email=email)

        code = OTPService.generate_otp(user.email)
        EmailService.send_verification_email(email, code)

        PendingLogin.objects.filter(user=user).delete()
        pending_login = PendingLogin.objects.create(user=user)
        return Response(
            {
                "message": "otp sent",
                "pending_token": str(pending_login.token),
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPEmailLoginView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = OTPVerifyLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        pending_login = get_object_or_404(PendingLogin, pending_token=serializer.validated_data["pending_token"])

        user = pending_login.user

        otp = serializer.validated_data["otp"]


        ok, msg = OTPService.verify_otp(user.email, otp)

        if not ok:
            return Response({"message": msg}, status=status.HTTP_400_BAD_REQUEST)

        OTPService.delete_otp(user.email)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


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


class TicketListCreateView(ListCreateAPIView):
    throttle_classes = [LoginThrottle]
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        serializer.is_valid()
        return Response(
            data={"message": "your ticket has been created"},
        )


class InstructorApplicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InstructorApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = InstructorService.submit_application(
            user=request.user,
            motivation=serializer.validated_data["motivation"],
        )

        return Response(
            {
                "detail": "your instructor application has been submitted",
                "application_id": application.id,
            },
            status=status.HTTP_201_CREATED,
        )

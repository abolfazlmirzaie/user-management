import re

from django.contrib.auth import (authenticate, get_user_model,
                                 password_validation)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers

from users.models import CustomUser, SubscriptionPlan
from .validators import PasswordValidator

User = get_user_model()


class UserRegisterSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)

    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords must match")


        validator = PasswordValidator()
        try:
            validator.validate(data["password1"])
        except ValidationError as e:
            raise serializers.ValidationError({"password1": e.messages})

        return data

    def create(self, validated_data):
        identifier = validated_data.pop("identifier")
        password = validated_data.pop("password1")
        validated_data.pop("password2")

        try:
            validate_email(identifier)

            user = User.objects.create_user(
                username=identifier,
                email=identifier,
                password=password,
                **validated_data
            )
        except ValidationError:
            user = User.objects.create_user(
                username=identifier,
                password=password,
                **validated_data
            )

        return user



class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        data["user"] = user
        return data


class UserEmailLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)


class OTPVerifyLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    code = serializers.CharField(max_length=6)


class EditUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser

        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "profile_picture",
        )
        extra_kwargs = {"password": {"write_only": True}}


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if (
            not User.objects.filter(email=value).exists()
            or not User.objects.get(email=value).is_verified
        ):
            raise serializers.ValidationError("Invalid email")
        return value

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = f"http://127.0.0.1:8000/api/auth/reset-password/{uid}/{token}/"
        print(reset_link)
        send_mail(
            subject="password reset",
            message=f"click on the link below to reset your password: /n{reset_link}",
            from_email=None,
            recipient_list=[user.email],
        )
        return reset_link


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)

    def __init__(self, *args, **kwargs):

        self.uid = kwargs.pop("uid", None)
        self.token = kwargs.pop("token", None)
        super().__init__(self, *args, **kwargs)

    def validate(self, attrs):
        try:
            uid = urlsafe_base64_decode(self.uid).decode()
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("user does not exist")

        if not PasswordResetTokenGenerator().check_token(self.user, self.token):
            raise serializers.ValidationError("the token is expired")

        return attrs

    def save(self, **kwargs):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
        return self.user




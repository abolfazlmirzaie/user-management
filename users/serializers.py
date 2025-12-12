import re

from django.contrib.auth import authenticate, get_user_model, password_validation
from rest_framework import serializers


User = get_user_model()


class UserRegisterSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)

    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords must match")

        password_validation.validate_password(data["password1"], user=None)
        return data

    def create(self, validated_data):
        identifier = validated_data.pop("identifier")
        password = validated_data.pop("password1")
        validated_data.pop("password2")

        if re.match(r"[^@]+@[^@]+\.[^@]+", identifier):
            user = User(email=identifier, **validated_data)
        else:
            user = User(username=identifier, **validated_data)

        user.set_password(password)
        user.save()
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

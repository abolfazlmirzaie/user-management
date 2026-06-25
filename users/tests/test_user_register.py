import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def register_url():
    return reverse("user-register")

@pytest.fixture
def valid_email_payload():

    return {
        "identifier": "testuser@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }


@pytest.fixture
def valid_username_payload():
    return {
        "identifier": "testuser123",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }



@pytest.mark.django_db
class TestUserRegisterSuccess:

    def test_register_with_email_returns_201(self, client, register_url, valid_email_payload):
        response = client.post(register_url, valid_email_payload)

        assert response.status_code == status.HTTP_201_CREATED

    def test_register_with_email_creates_user(self, client, register_url, valid_email_payload):
        """ثبت‌نام با ایمیل باید یوزر در دیتابیس بسازه"""
        client.post(register_url, valid_email_payload)

        assert User.objects.filter(email="testuser@example.com").exists()

    def test_register_with_email_sets_email_field(self, client, register_url, valid_email_payload):
        """وقتی identifier ایمیله، فیلد email یوزر باید پر بشه"""
        client.post(register_url, valid_email_payload)

        user = User.objects.get(username="testuser@example.com")
        assert user.email == "testuser@example.com"

    def test_register_with_username_returns_201(self, client, register_url, valid_username_payload):
        """ثبت‌نام با یوزرنیم معتبر باید 201 برگردونه"""
        response = client.post(register_url, valid_username_payload)

        assert response.status_code == status.HTTP_201_CREATED

    def test_register_with_username_creates_user(self, client, register_url, valid_username_payload):
        """ثبت‌نام با یوزرنیم باید یوزر در دیتابیس بسازه"""
        client.post(register_url, valid_username_payload)

        assert User.objects.filter(username="testuser123").exists()

    def test_register_response_contains_message(self, client, register_url, valid_email_payload):
        """پاسخ باید message داشته باشه"""
        response = client.post(register_url, valid_email_payload)

        assert "message" in response.data

    def test_register_logs_user_in(self, client, register_url, valid_email_payload):
        """بعد از ثبت‌نام، یوزر باید login شده باشه (session داشته باشه)"""
        response = client.post(register_url, valid_email_payload)

        assert "_auth_user_id" in response.wsgi_request.session



@pytest.mark.django_db
class TestUserRegisterValidation:

    def test_mismatched_passwords_returns_400(self, client, register_url):
        """پسوردهای متفاوت باید 400 برگردونه"""
        payload = {
            "identifier": "user@example.com",
            "password1": "StrongPass123!",
            "password2": "DifferentPass123!",
        }
        response = client.post(register_url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_mismatched_passwords_returns_error_message(self, client, register_url):
        """پیام خطای پسورد باید در response باشه"""
        payload = {
            "identifier": "user@example.com",
            "password1": "StrongPass123!",
            "password2": "DifferentPass123!",
        }
        response = client.post(register_url, payload)

        assert "Passwords must match" in str(response.data)

    def test_weak_password_returns_400(self, client, register_url):
        """پسورد ضعیف باید 400 برگردونه"""
        payload = {
            "identifier": "user@example.com",
            "password1": "123",
            "password2": "123",
        }
        response = client.post(register_url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_identifier_returns_400(self, client, register_url):
        """نبود identifier باید 400 برگردونه"""
        payload = {
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = client.post(register_url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_password_returns_400(self, client, register_url):
        """نبود پسورد باید 400 برگردونه"""
        payload = {
            "identifier": "user@example.com",
        }
        response = client.post(register_url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_email_returns_400(self, client, register_url, valid_email_payload):
        """ثبت‌نام دوباره با ایمیل تکراری باید 400 برگردونه"""
        # اول یوزر بساز
        client.post(register_url, valid_email_payload)

        # دوباره همون ایمیل رو ثبت‌نام کن
        response = client.post(register_url, valid_email_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_payload_returns_400(self, client, register_url):
        """payload خالی باید 400 برگردونه"""
        response = client.post(register_url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
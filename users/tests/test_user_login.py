import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import PendingLogin

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def login_url():
    return reverse("user-login")

@pytest.fixture
def user_fixture(request):
    user = User.objects.create_user(username="test", password="logintest123")
    return user

@pytest.fixture
def user_fixture_2(request):
    user = User.objects.create_user(username="test2", password="2fauser")
    user.two_factor_enabled = True
    user.save()
    return user


@pytest.mark.django_db
class TestUserLogin:
    def test_user_already_login(self, client, login_url, user_fixture):
        client.force_authenticate(user=user_fixture)

        response = client.post(login_url, {})
        assert "you are already logged in" in str(response.data)



    def test_successful_login(self, client, login_url, user_fixture):

        response = client.post(login_url, {"username": user_fixture.username, "password" : "logintest123"})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_send_otp(self, client, login_url, user_fixture_2):
        response = client.post(login_url, {"username": user_fixture_2.username, "password": "2fauser"})
        assert response.status_code == status.HTTP_200_OK
        assert PendingLogin.objects.filter(user=user_fixture_2).exists()
        assert "pending_token" in response.data


    def test_blank_password(self, client, login_url, user_fixture):
        response = client.post(login_url, {"username": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "blank" in str(response.data).lower()


    def test_blank_username(self, client, login_url, user_fixture):
        response = client.post(login_url, {"password": "logintest123"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "required" in str(response.data).lower()


    def test_blank_data(self, client, login_url, user_fixture):
        response = client.post(login_url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "required" in str(response.data).lower()
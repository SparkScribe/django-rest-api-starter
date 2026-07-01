import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def auth_client(api_client, user):
    response = api_client.post(
        "/api/v1/auth/token/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return api_client

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_obtain_jwt_token(api_client, user):
    response = api_client.post(
        "/api/v1/auth/token/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_refresh_token(api_client, user):
    token_response = api_client.post(
        "/api/v1/auth/token/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )
    response = api_client.post(
        "/api/v1/auth/token/refresh/",
        {"refresh": token_response.data["refresh"]},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data

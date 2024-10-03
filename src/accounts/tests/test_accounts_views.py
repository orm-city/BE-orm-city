import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import CustomUser, UserActivity
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(username="testuser", password="testpass123"):
        return CustomUser.objects.create_user(username=username, password=password)

    return make_user


@pytest.mark.django_db
def test_register_view(api_client):
    url = reverse("accounts:register")
    data = {
        "username": "newuser",
        "password": "newpass123",
        "password2": "newpass123",
        "email": "newuser@example.com",
        "first_name": "New",  # 추가됨
        "last_name": "User",  # 추가됨
    }
    response = api_client.post(url, data)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(username="newuser").exists()
    assert UserActivity.objects.filter(user__username="newuser").exists()


@pytest.mark.django_db
def test_logout_view(api_client, create_user):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    url = reverse("accounts:logout")
    data = {"refresh": str(refresh)}
    response = api_client.post(url, data)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    assert response.status_code == status.HTTP_205_RESET_CONTENT


@pytest.mark.django_db
def test_logout_view(api_client, create_user):  # noqa
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    url = reverse("accounts:logout")
    data = {"refresh": str(refresh)}
    response = api_client.post(url, data)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    assert response.status_code == status.HTTP_205_RESET_CONTENT


@pytest.mark.django_db
def test_user_profile_view(api_client, create_user):
    user = create_user()
    api_client.force_authenticate(user=user)
    url = reverse("accounts:profile")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == "testuser"

    update_data = {"first_name": "Updated", "last_name": "User"}
    response = api_client.patch(url, update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["first_name"] == "Updated"
    assert response.data["last_name"] == "User"


@pytest.mark.django_db
def test_user_activity_list_view(api_client, create_user):
    user = create_user()
    UserActivity.objects.create(user=user, ip_address="127.0.0.1")
    api_client.force_authenticate(user=user)
    url = reverse("accounts:activity")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_delete_account_view(api_client, create_user):
    user = create_user()
    api_client.force_authenticate(user=user)
    url = reverse("accounts:delete")
    data = {"password": "testpass123"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert not user.is_active


@pytest.mark.django_db
def test_delete_account_view_wrong_password(api_client, create_user):
    user = create_user()
    api_client.force_authenticate(user=user)
    url = reverse("accounts:delete")
    data = {"password": "wrongpassword"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user.refresh_from_db()
    assert user.is_active

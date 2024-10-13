import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import CustomUser, UserActivity


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword",
    }


@pytest.fixture
def create_user(user_data):
    return CustomUser.objects.create_user(**user_data)


@pytest.mark.django_db
class TestUserManagementViewSet:
    @pytest.fixture
    def admin_user(self):
        return CustomUser.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="adminpass",
            role="admin",
        )

    def test_list_users_as_admin(self, api_client, admin_user):
        # GIVEN
        api_client.force_authenticate(user=admin_user)

        # WHEN
        response = api_client.get(reverse("user-list"))

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_list_users_as_student(self, api_client, create_user):
        # GIVEN
        user = create_user
        api_client.force_authenticate(user=user)

        # WHEN
        response = api_client.get(reverse("user-list"))

        # THEN
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_user_as_admin(self, api_client, admin_user, create_user):
        # GIVEN
        user = create_user
        api_client.force_authenticate(user=admin_user)

        # WHEN
        response = api_client.get(reverse("user-detail", kwargs={"pk": user.pk}))

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username

    def test_retrieve_own_user_as_student(self, api_client, create_user):
        # GIVEN
        user = create_user
        api_client.force_authenticate(user=user)

        # WHEN
        response = api_client.get(reverse("user-detail", kwargs={"pk": user.pk}))

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username

    def test_retrieve_other_user_as_student(self, api_client, create_user):
        # GIVEN
        user1 = create_user
        user2 = CustomUser.objects.create_user(
            email="user2@example.com", username="user2", password="testpass"
        )
        api_client.force_authenticate(user=user1)

        # WHEN
        response = api_client.get(reverse("user-detail", kwargs={"pk": user2.pk}))

        # THEN
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestRegisterView:
    def test_register_user(self, api_client, user_data):
        # GIVEN
        url = reverse("register")

        # WHEN
        response = api_client.post(url, user_data)

        # THEN
        assert response.status_code == status.HTTP_201_CREATED
        assert "user" in response.data
        assert "refresh" in response.data
        assert "access" in response.data


@pytest.mark.django_db
class TestLoginView:
    def test_login_user(self, api_client, create_user, user_data):
        # GIVEN
        url = reverse("login")
        user = create_user  # noqa

        # WHEN
        response = api_client.post(
            url, {"email": user_data["email"], "password": user_data["password"]}
        )

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert "user" in response.data
        assert "refresh" in response.data
        assert "access" in response.data


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_user(self, api_client, create_user):
        # GIVEN
        user = create_user
        api_client.force_authenticate(user=user)
        refresh = api_client.post(
            reverse("login"), {"email": user.email, "password": "testpassword"}
        ).data["refresh"]

        # WHEN
        response = api_client.post(reverse("logout"), {"refresh_token": refresh})

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Successfully logged out."


@pytest.mark.django_db
class TestUserProfileView:
    def test_retrieve_user_profile(self, api_client, create_user):
        # GIVEN
        user = create_user
        api_client.force_authenticate(user=user)

        # WHEN
        response = api_client.get(reverse("profile"))

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username

    def test_update_user_profile(self, api_client, create_user):
        # GIVEN
        user = create_user
        api_client.force_authenticate(user=user)
        update_data = {"username": "newusername"}

        # WHEN
        response = api_client.patch(reverse("profile"), update_data)

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "newusername"


@pytest.mark.django_db
class TestUserActivityListView:
    def test_list_user_activities(self, api_client, create_user):
        # GIVEN
        user = create_user
        api_client.force_authenticate(user=user)
        UserActivity.objects.create(user=user)

        # WHEN
        response = api_client.get(reverse("activity"))

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


@pytest.mark.django_db
class TestDeleteAccountView:
    def test_delete_account(self, api_client, create_user):
        # GIVEN
        user = create_user
        api_client.force_authenticate(user=user)

        # WHEN
        response = api_client.delete(reverse("delete"))

        # THEN
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert CustomUser.objects.count() == 0


@pytest.mark.django_db
class TestManagerCreationView:
    def test_create_manager(self, api_client):
        # GIVEN
        admin = CustomUser.objects.create_superuser(
            email="admin@example.com", username="admin", password="adminpass"
        )
        api_client.force_authenticate(user=admin)
        manager_data = {
            "email": "manager@example.com",
            "username": "manager",
            "password": "managerpass",
        }

        # WHEN
        response = api_client.post(reverse("create_manager"), manager_data)

        # THEN
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["role"] == "manager"


@pytest.mark.django_db
class TestChangeUserRoleView:
    def test_change_user_role(self, api_client, create_user):
        # GIVEN
        user = create_user
        admin = CustomUser.objects.create_superuser(
            email="admin@example.com", username="admin", password="adminpass"
        )
        api_client.force_authenticate(user=admin)

        # WHEN
        response = api_client.patch(
            reverse("change_role", kwargs={"user_id": user.id}), {"role": "manager"}
        )

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == "manager"

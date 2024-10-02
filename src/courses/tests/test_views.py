import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from courses.models import MajorCategory, MinorCategory, Enrollment
from accounts.models import CustomUser


@pytest.mark.django_db
class TestCoursesViews:
    @pytest.fixture
    def user(self):
        return CustomUser.objects.create_user(
            username="testuser", password="testpass123"
        )

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, user):
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return client

    @pytest.fixture
    def major_category(self):
        return MajorCategory.objects.create(name="Web Development", price=50000)

    @pytest.fixture
    def minor_category(self, major_category):
        return MinorCategory.objects.create(
            name="HTML/CSS",
            major_category=major_category,
            content="Learn HTML/CSS",
            order=1,
        )

    @pytest.fixture
    def enrollment(self, user, major_category):
        return Enrollment.objects.create(
            user=user,
            major_category=major_category,
            expiry_date=timezone.now() + timezone.timedelta(days=30),
        )

    def test_major_category_list_view(self, authenticated_client, major_category):
        url = reverse("major-category-list")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == major_category.name
        assert response.data[0]["price"] == major_category.price

    def test_minor_category_list_view(
        self, authenticated_client, major_category, minor_category
    ):
        url = reverse(
            "minor-category-list", kwargs={"major_category_id": major_category.id}
        )
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == minor_category.name
        assert response.data[0]["major_category"] == major_category.id
        assert response.data[0]["content"] == minor_category.content
        assert response.data[0]["order"] == minor_category.order

    def test_user_enrollment_list_view(self, authenticated_client, user, enrollment):
        url = reverse("user-enrollment-list")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["major_category"]["id"] == enrollment.major_category.id
        assert (
            response.data[0]["major_category"]["name"] == enrollment.major_category.name
        )
        assert response.data[0]["user"] == user.id
        assert "enrollment_date" in response.data[0]
        assert "expiry_date" in response.data[0]
        assert response.data[0]["status"] == enrollment.status

    def test_user_enrollment_list_view_unauthenticated(self, api_client):
        url = reverse("user-enrollment-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

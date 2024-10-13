import pytest
from datetime import timedelta

from django.utils import timezone
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import CustomUser
from courses.models import MajorCategory, MinorCategory, Enrollment


@pytest.mark.django_db
class TestCoursesViews:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        return CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass123"
        )

    @pytest.fixture
    def admin_user(self):
        return CustomUser.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

    @pytest.fixture
    def admin_or_manager_user(self):
        return CustomUser.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="password",
            role="manager",
        )

    @pytest.fixture
    def major_category(self):
        return MajorCategory.objects.create(name="Web Development", price=50000)

    @pytest.fixture
    def minor_category(self, major_category):
        return MinorCategory.objects.create(
            name="HTML/CSS",
            major_category=major_category,
            content="Learn HTML and CSS",
            order=1,
        )

    @pytest.fixture
    def enrollment(self, user, major_category):
        return Enrollment.objects.create(
            user=user,
            major_category=major_category,
            expiry_date=timezone.now() + timedelta(days=365),
        )

    def test_major_category_list(self, api_client, major_category):
        url = reverse("majorcategory-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_major_category_create(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("majorcategory-list")
        data = {"name": "Data Science", "price": 60000}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert MajorCategory.objects.count() == 1

    def test_major_category_details(
        self, api_client, major_category, minor_category, enrollment, user
    ):
        api_client.force_authenticate(user=user)
        url = reverse("majorcategory-details", kwargs={"pk": major_category.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "total_video_count" in response.data

    def test_minor_category_list(self, api_client, minor_category):
        url = reverse("minorcategory-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_minor_category_list_filtered(
        self, api_client, minor_category, major_category
    ):
        url = reverse("minorcategory-list")
        response = api_client.get(url, {"major_category_id": major_category.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == minor_category.name

    def test_minor_category_by_major(self, api_client, minor_category, major_category):
        url = reverse("minorcategory-by-major", kwargs={"major_id": major_category.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == minor_category.name

    def test_enrollment_create(self, api_client, user, major_category):
        api_client.force_authenticate(user=user)
        url = reverse("enrollment-list")
        data = {"major_category": major_category.pk}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Enrollment.objects.count() == 1

    def test_complete_enrollment(
        self, api_client, admin_or_manager_user, enrollment, major_category
    ):
        api_client.force_authenticate(user=admin_or_manager_user)
        url = reverse("enrollment-complete-enrollment", kwargs={"pk": enrollment.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        updated_enrollment = Enrollment.objects.get(pk=enrollment.pk)
        assert updated_enrollment.status == "completed"

    def test_enrollment_list_admin(self, api_client, admin_user, enrollment):
        api_client.force_authenticate(user=admin_user)
        url = reverse("enrollment-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_enrollment_list_user(self, api_client, user, enrollment):
        api_client.force_authenticate(user=user)
        url = reverse("enrollment-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

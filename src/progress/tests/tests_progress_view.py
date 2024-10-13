import pytest

from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from progress.models import UserProgress
from courses.models import Enrollment, MinorCategory, MajorCategory
from videos.models import Video


@pytest.mark.django_db
class TestUserProgressUpdateView:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self, django_user_model):
        return django_user_model.objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )

    @pytest.fixture
    def major_category(self):
        return MajorCategory.objects.create(name="Test Major Category")

    @pytest.fixture
    def minor_category(self, major_category):
        return MinorCategory.objects.create(
            name="Test Minor Category", major_category=major_category, order=1
        )

    @pytest.fixture
    def video(self, minor_category):
        return Video.objects.create(
            name="Test Video",
            minor_category=minor_category,
            duration=timedelta(minutes=5),
        )

    @pytest.fixture
    def user_progress(self, user, video):
        return UserProgress.objects.create(
            user=user, video=video, progress_percent=50, total_duration=423432
        )

    @pytest.fixture
    def enrollment(self, user, major_category):
        return Enrollment.objects.create(
            user=user, major_category=major_category, status="active"
        )

    def test_update_progress_success(self, api_client, user, user_progress, enrollment):
        # Given
        api_client.force_authenticate(user=user)
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": 10, "last_position": 60}

        # When
        response = api_client.patch(url, data)

        # Then
        assert response.status_code == status.HTTP_200_OK
        updated_progress = UserProgress.objects.get(pk=user_progress.pk)
        assert updated_progress.total_duration == 110
        assert updated_progress.last_position == 60

    def test_update_progress_inactive_enrollment(
        self, api_client, user, user_progress, enrollment
    ):
        # Given
        enrollment.status = "inactive"
        enrollment.save()
        api_client.force_authenticate(user=user)
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": 10, "last_position": 60}

        # When
        response = api_client.patch(url, data)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Enrollment is not active"

    def test_update_progress_no_enrollment(self, api_client, user, user_progress):
        # Given
        api_client.force_authenticate(user=user)
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": 10, "last_position": 60}

        # When
        response = api_client.patch(url, data)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["error"]
            == "No valid enrollment found for this user and video"
        )

    def test_update_progress_invalid_data(
        self, api_client, user, user_progress, enrollment
    ):
        # Given
        api_client.force_authenticate(user=user)
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": "invalid", "last_position": "invalid"}

        # When
        response = api_client.patch(url, data)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "additional_time" in response.data
        assert "last_position" in response.data

    def test_update_progress_unauthenticated(self, api_client, user_progress):
        # Given
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": 10, "last_position": 60}

        # When
        response = api_client.patch(url, data)

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

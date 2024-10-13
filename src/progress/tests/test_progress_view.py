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
    """
    UserProgress 업데이트 관련 API 테스트 클래스.
    
    이 클래스는 사용자의 학습 진척도를 업데이트하는 API를 테스트합니다.
    """

    @pytest.fixture
    def api_client(self):
        """
        API 클라이언트를 생성하여 반환하는 pytest fixture.

        Returns:
            APIClient: API 테스트를 위한 클라이언트 객체.
        """
        return APIClient()

    @pytest.fixture
    def user(self, django_user_model):
        """
        테스트용 사용자 생성 fixture.

        Args:
            django_user_model: Django 사용자 모델.

        Returns:
            User: 생성된 테스트 사용자 객체.
        """
        return django_user_model.objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )

    @pytest.fixture
    def major_category(self):
        """
        테스트용 MajorCategory 생성 fixture.

        Returns:
            MajorCategory: 생성된 MajorCategory 객체.
        """
        return MajorCategory.objects.create(name="Test Major Category")

    @pytest.fixture
    def minor_category(self, major_category):
        """
        테스트용 MinorCategory 생성 fixture.

        Args:
            major_category: 테스트용 MajorCategory 객체.

        Returns:
            MinorCategory: 생성된 MinorCategory 객체.
        """
        return MinorCategory.objects.create(
            name="Test Minor Category", major_category=major_category, order=1
        )

    @pytest.fixture
    def video(self, minor_category):
        """
        테스트용 Video 생성 fixture.

        Args:
            minor_category: 테스트용 MinorCategory 객체.

        Returns:
            Video: 생성된 Video 객체.
        """
        return Video.objects.create(
            name="Test Video",
            minor_category=minor_category,
            duration=timedelta(minutes=5),
        )

    @pytest.fixture
    def user_progress(self, user, video):
        """
        테스트용 UserProgress 생성 fixture.

        Args:
            user: 테스트용 사용자 객체.
            video: 테스트용 Video 객체.

        Returns:
            UserProgress: 생성된 UserProgress 객체.
        """
        return UserProgress.objects.create(
            user=user, video=video, progress_percent=50, total_duration=423432
        )

    @pytest.fixture
    def enrollment(self, user, major_category):
        """
        테스트용 Enrollment 생성 fixture.

        Args:
            user: 테스트용 사용자 객체.
            major_category: 테스트용 MajorCategory 객체.

        Returns:
            Enrollment: 생성된 Enrollment 객체.
        """
        return Enrollment.objects.create(
            user=user, major_category=major_category, status="active"
        )

    def test_update_progress_success(self, api_client, user, user_progress, enrollment):
        """
        진척도를 성공적으로 업데이트하는 테스트.

        사용자가 정상적인 데이터를 제공하여 진척도를 업데이트할 수 있는지 확인합니다.
        """
        api_client.force_authenticate(user=user)
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": 10, "last_position": 60}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        updated_progress = UserProgress.objects.get(pk=user_progress.pk)
        assert updated_progress.total_duration == 110
        assert updated_progress.last_position == 60

    def test_update_progress_inactive_enrollment(self, api_client, user, user_progress, enrollment):
        """
        비활성화된 수강 상태에서 진척도 업데이트 실패 테스트.

        사용자가 등록 상태가 비활성화된 경우 진척도 업데이트가 실패하는지 확인합니다.
        """
        enrollment.status = "inactive"
        enrollment.save()
        api_client.force_authenticate(user=user)
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": 10, "last_position": 60}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Enrollment is not active"

    def test_update_progress_no_enrollment(self, api_client, user, user_progress):
        """
        수강 등록이 없는 경우 진척도 업데이트 실패 테스트.

        사용자가 수강 등록이 없을 때 진척도 업데이트가 실패하는지 확인합니다.
        """
        api_client.force_authenticate(user=user)
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": 10, "last_position": 60}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "No valid enrollment found for this user and video"

    def test_update_progress_invalid_data(self, api_client, user, user_progress, enrollment):
        """
        잘못된 데이터를 제공할 때 진척도 업데이트 실패 테스트.

        사용자가 잘못된 데이터를 제공했을 때, API가 적절한 오류를 반환하는지 확인합니다.
        """
        api_client.force_authenticate(user=user)
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": "invalid", "last_position": "invalid"}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "additional_time" in response.data
        assert "last_position" in response.data

    def test_update_progress_unauthenticated(self, api_client, user_progress):
        """
        인증되지 않은 사용자가 진척도 업데이트를 시도할 때 실패하는지 테스트.

        인증되지 않은 사용자가 API를 호출할 때 401 응답을 반환하는지 확인합니다.
        """
        url = reverse("user-progress-update", kwargs={"pk": user_progress.pk})
        data = {"additional_time": 10, "last_position": 60}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

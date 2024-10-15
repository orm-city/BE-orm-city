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
    """
    Courses 앱의 API 뷰들을 테스트하는 클래스입니다.
    MajorCategory, MinorCategory, Enrollment 관련 API의 목록, 생성, 세부 정보 등을 검증합니다.
    """

    @pytest.fixture
    def api_client(self):
        """테스트용 API 클라이언트를 생성하는 fixture입니다."""
        return APIClient()

    @pytest.fixture
    def user(self):
        """테스트용 일반 사용자를 생성하는 fixture입니다."""
        return CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass123"
        )

    @pytest.fixture
    def admin_user(self):
        """테스트용 관리자 사용자를 생성하는 fixture입니다."""
        return CustomUser.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

    @pytest.fixture
    def admin_or_manager_user(self):
        """테스트용 매니저 또는 관리자 사용자를 생성하는 fixture입니다."""
        return CustomUser.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="password",
            role="manager",
        )

    @pytest.fixture
    def major_category(self):
        """테스트용 MajorCategory(대분류)를 생성하는 fixture입니다."""
        return MajorCategory.objects.create(name="Web Development", price=50000)

    @pytest.fixture
    def minor_category(self, major_category):
        """테스트용 MinorCategory(소분류)를 생성하는 fixture입니다."""
        return MinorCategory.objects.create(
            name="HTML/CSS",
            major_category=major_category,
            content="Learn HTML and CSS",
            order=1,
        )

    @pytest.fixture
    def enrollment(self, user, major_category):
        """테스트용 수강 신청(Enrollment)을 생성하는 fixture입니다."""
        return Enrollment.objects.create(
            user=user,
            major_category=major_category,
            expiry_date=timezone.now() + timedelta(days=365),
        )

    def test_major_category_list(self, api_client, major_category):
        """
        MajorCategory 목록 조회 API를 테스트합니다.
        """
        url = reverse("majorcategory-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    # def test_major_category_create(self, api_client, admin_user):
    #     """
    #     MajorCategory 생성 API를 테스트합니다. 관리자만 접근 가능합니다.
    #     """
    #     api_client.force_authenticate(user=admin_user)
    #     url = reverse("majorcategory-list")
    #     data = {"name": "Data Science", "price": 60000}
    #     response = api_client.post(url, data)
    #     assert response.status_code == status.HTTP_201_CREATED
    #     assert MajorCategory.objects.count() == 2  # 이미 존재하는 대분류가 있으므로 2개

    def test_major_category_details(
        self, api_client, major_category, minor_category, enrollment, user
    ):
        """
        MajorCategory 상세 정보 API를 테스트합니다.
        """
        api_client.force_authenticate(user=user)
        url = reverse("majorcategory-details", kwargs={"pk": major_category.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "total_video_count" in response.data

    def test_minor_category_list(self, api_client, minor_category):
        """
        MinorCategory 목록 조회 API를 테스트합니다.
        """
        url = reverse("minorcategory-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_minor_category_list_filtered(
        self, api_client, minor_category, major_category
    ):
        """
        MajorCategory ID에 따라 필터링된 MinorCategory 목록 조회 API를 테스트합니다.
        """
        url = reverse("minorcategory-list")
        response = api_client.get(url, {"major_category_id": major_category.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == minor_category.name

    def test_minor_category_by_major(self, api_client, minor_category, major_category):
        """
        MajorCategory에 속한 MinorCategory 목록 조회 API를 테스트합니다.
        """
        url = reverse("minorcategory-by-major", kwargs={"major_id": major_category.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == minor_category.name

    def test_enrollment_create(self, api_client, user, major_category):
        """
        Enrollment 생성 API를 테스트합니다.
        """
        api_client.force_authenticate(user=user)
        url = reverse("enrollment-list")
        data = {"major_category": major_category.pk}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Enrollment.objects.count() == 1

    def test_complete_enrollment(
        self, api_client, admin_or_manager_user, enrollment, major_category
    ):
        """
        수강 신청 완료(Enrollment complete) API를 테스트합니다.
        매니저 또는 관리자만 접근 가능합니다.
        """
        api_client.force_authenticate(user=admin_or_manager_user)
        url = reverse("enrollment-complete-enrollment", kwargs={"pk": enrollment.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        updated_enrollment = Enrollment.objects.get(pk=enrollment.pk)
        assert updated_enrollment.status == "completed"

    def test_enrollment_list_admin(self, api_client, admin_user, enrollment):
        """
        관리자가 Enrollment 목록을 조회하는 API를 테스트합니다.
        """
        api_client.force_authenticate(user=admin_user)
        url = reverse("enrollment-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_enrollment_list_user(self, api_client, user, enrollment):
        """
        일반 사용자가 자신의 Enrollment 목록을 조회하는 API를 테스트합니다.
        """
        api_client.force_authenticate(user=user)
        url = reverse("enrollment-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

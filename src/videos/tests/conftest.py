import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from videos.models import Video, MinorCategory
from courses.models import MajorCategory, Enrollment

from unittest.mock import patch

from django.utils import timezone
from datetime import timedelta



@pytest.fixture
def api_client():
    return APIClient()


# 사용자 관련 fixture
@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", password="password", email="admin@example.com", role="admin"
    )


@pytest.fixture
def normal_user(db):
    User = get_user_model()
    return User.objects.create_user(username="user", password="password")


@pytest.fixture
def student_user(db):
    User = get_user_model()
    return User.objects.create_user(username="student", password="password")


# 대분류(MajorCategory) fixture
@pytest.fixture
def major_category(db):
    return MajorCategory.objects.create(name="Web Development", price=100000)


# 소분류(MinorCategory) fixture
@pytest.fixture
def minor_category(db, major_category):
    return MinorCategory.objects.create(
        name="HTML/CSS",
        major_category=major_category,
        content="Learn HTML and CSS",
        order=1,
    )


# 비디오(Video) fixture
@pytest.fixture
def video(db, minor_category):
    return Video.objects.create(
        name="Test Video",
        description="Test Description",
        video_url="https://example.com/test.mp4",
        minor_category=minor_category,
    )


# 수강신청(Enrollment) fixture
@pytest.fixture
def enrollment(db, normal_user, major_category):
    return Enrollment.objects.create(
        user=normal_user,
        major_category=major_category,
        enrollment_date=timezone.now(),
        expiry_date=timezone.now() + timedelta(days=30),
        status="active",
    )


# 여러 비디오 데이터를 쉽게 생성할 수 있는 factory fixture
@pytest.fixture
def video_factory(db, minor_category):
    def create_videos(num):
        return [
            Video.objects.create(
                name=f"Test Video {i}",
                description=f"Description {i}",
                video_url=f"https://example.com/test{i}.mp4",
                minor_category=minor_category,
            )
            for i in range(num)
        ]

    return create_videos


# S3 클라이언트를 mocking하는 fixture
@pytest.fixture
def mock_s3_client():
    with patch("videos.services.get_s3_client") as mock_s3:
        yield mock_s3


# 인증된 클라이언트를 반환하는 helper fixture
@pytest.fixture
def client_with_credentials(api_client):
    def get_authenticated_client(user):
        api_client.force_authenticate(user=user)
        return api_client

    return get_authenticated_client

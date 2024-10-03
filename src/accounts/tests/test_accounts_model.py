import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import UserActivity

CustomUser = get_user_model()


@pytest.mark.django_db
def test_create_custom_user():
    user = CustomUser.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        role="student",
        nickname="테스트닉네임",
        gender="M",
        contact_number="010-1234-5678",
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "student"
    assert user.nickname == "테스트닉네임"
    assert user.gender == "M"
    assert user.contact_number == "010-1234-5678"
    assert user.total_study_time == timezone.timedelta()


@pytest.mark.django_db
def test_custom_user_str_method():
    user = CustomUser.objects.create_user(username="testuser", email="test@example.com")
    assert str(user) == "testuser"


@pytest.mark.django_db
def test_custom_user_invalid_role():
    with pytest.raises(ValidationError):
        user = CustomUser(
            username="testuser", email="test@example.com", role="invalid_role"
        )
        user.full_clean()


@pytest.mark.django_db
def test_custom_user_invalid_phone_number():
    with pytest.raises(ValidationError):
        user = CustomUser(
            username="testuser",
            email="test@example.com",
            contact_number="1234567890",  # 올바르지 않은 형식
        )
        user.full_clean()


@pytest.mark.django_db
def test_create_user_activity():
    user = CustomUser.objects.create_user(username="testuser", email="test@example.com")
    activity = UserActivity.objects.create(user=user, ip_address="127.0.0.1")
    assert activity.user == user
    assert activity.ip_address == "127.0.0.1"
    assert activity.login_time is not None
    assert activity.logout_time is None


@pytest.mark.django_db
def test_user_activity_str_method():
    user = CustomUser.objects.create_user(username="testuser", email="test@example.com")
    activity = UserActivity.objects.create(user=user, ip_address="127.0.0.1")
    assert str(activity) == f"testuser - {activity.login_time}"


@pytest.mark.django_db
def test_user_activity_relationship():
    user = CustomUser.objects.create_user(username="testuser", email="test@example.com")
    activity = UserActivity.objects.create(user=user, ip_address="127.0.0.1")
    assert user.activities.first() == activity

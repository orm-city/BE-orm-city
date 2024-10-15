import pytest

from django.utils import timezone

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from accounts.models import UserActivity


User = get_user_model()


@pytest.mark.django_db
class TestCustomUser:
    """
    CustomUser 모델을 테스트하는 클래스입니다.
    사용자 생성, 슈퍼유저 생성, 문자열 표현 등을 테스트합니다.
    """

    def test_create_user(self):
        """
        일반 사용자를 생성하고, 올바르게 생성되었는지 검증합니다.
        """
        # GIVEN
        email = "test@example.com"
        username = "testuser"
        password = "testpass123"

        # WHEN
        user = User.objects.create_user(
            email=email, username=username, password=password
        )

        # THEN
        assert user.email == email
        assert user.username == username
        assert user.role == "student"  # default role
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        """
        슈퍼유저를 생성하고, 올바르게 생성되었는지 검증합니다.
        """
        # GIVEN
        email = "admin@example.com"
        username = "admin"
        password = "adminpass123"

        # WHEN
        admin = User.objects.create_superuser(
            email=email, username=username, password=password
        )

        # THEN
        assert admin.email == email
        assert admin.username == username
        assert admin.role == "admin"
        assert admin.is_active
        assert admin.is_staff
        assert admin.is_superuser

    def test_user_str_representation(self):
        """
        사용자 객체의 문자열 표현이 올바른지 테스트합니다.
        """
        # GIVEN
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

        # WHEN
        user_str = str(user)

        # THEN
        assert user_str == "testuser (학생)"

    def test_create_user_without_email(self):
        """
        이메일 없이 사용자를 생성할 때 발생하는 예외를 테스트합니다.
        """
        # GIVEN
        email = ""
        username = "testuser"
        password = "testpass123"

        # WHEN / THEN
        with pytest.raises(ValueError, match="The Email field must be set"):
            User.objects.create_user(email=email, username=username, password=password)

    @pytest.mark.parametrize("role", ["student", "manager", "admin"])
    def test_valid_roles(self, role):
        """
        유효한 역할로 사용자를 생성하고, 역할이 올바르게 설정되었는지 테스트합니다.
        """
        # GIVEN
        email = f"{role}@example.com"
        username = f"{role}user"
        password = "testpass123"

        # WHEN
        user = User.objects.create_user(
            email=email, username=username, password=password, role=role
        )

        # THEN
        assert user.role == role

    def test_invalid_role(self):
        """
        잘못된 역할을 지정한 사용자를 생성할 때 발생하는 예외를 테스트합니다.
        """
        # GIVEN
        email = "invalid@example.com"
        username = "invaliduser"
        password = "testpass123"
        invalid_role = "invalid_role"

        # WHEN
        user = User.objects.create_user(
            email=email, username=username, password=password, role=invalid_role
        )

        # THEN
        with pytest.raises(ValidationError):
            user.full_clean()

    def test_email_as_username_field(self):
        """
        이메일이 사용자 이름 필드로 사용되는지 테스트합니다.
        """
        # GIVEN
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

        # WHEN/THEN
        assert user.USERNAME_FIELD == "email"
        assert user.get_username() == "test@example.com"

    def test_required_fields(self):
        """
        필수 필드들이 올바르게 설정되었는지 테스트합니다.
        """
        # GIVEN/WHEN/THEN
        assert "username" in User.REQUIRED_FIELDS
        assert (
            "email" not in User.REQUIRED_FIELDS
        )  # email is the USERNAME_FIELD, so it's not in REQUIRED_FIELDS


@pytest.mark.django_db
class TestUserActivity:
    """
    UserActivity 모델을 테스트하는 클래스입니다.
    사용자 활동 생성, 문자열 표현, 로그아웃 기록 등을 테스트합니다.
    """

    @pytest.fixture
    def user(self):
        """
        테스트용 사용자 객체를 생성하는 픽스처입니다.
        """
        return User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

    def test_create_user_activity(self, user):
        """
        사용자의 활동 기록을 생성하고, 올바르게 생성되었는지 테스트합니다.
        """
        # GIVEN
        # User fixture

        # WHEN
        activity = UserActivity.objects.create(user=user)

        # THEN
        assert activity.user == user
        assert activity.login_time is not None
        assert activity.logout_time is None

    def test_user_activity_str_representation(self, user):
        """
        활동 객체의 문자열 표현이 올바른지 테스트합니다.
        """
        # GIVEN
        activity = UserActivity.objects.create(user=user)

        # WHEN
        activity_str = str(activity)

        # THEN
        expected_str = f"{user.username}의 활동 - 로그인: {activity.login_time}"
        assert activity_str == expected_str

    def test_user_activity_with_logout(self, user):
        """
        로그아웃 시간을 기록하고, 올바르게 저장되었는지 테스트합니다.
        """
        # GIVEN
        activity = UserActivity.objects.create(user=user)
        logout_time = timezone.now()

        # WHEN
        activity.logout_time = logout_time
        activity.save()

        # THEN
        assert activity.logout_time == logout_time

    def test_multiple_activities_for_user(self, user):
        """
        동일한 사용자에 대해 여러 활동 기록을 생성하고, 올바르게 저장되었는지 테스트합니다.
        """
        # GIVEN
        # User fixture

        # WHEN
        UserActivity.objects.create(user=user)
        UserActivity.objects.create(user=user)

        # THEN
        activities = UserActivity.objects.filter(user=user)
        assert activities.count() == 2

    def test_activity_ordering(self, user):
        """
        활동 기록이 로그인 시간 순으로 올바르게 정렬되는지 테스트합니다.
        """
        # GIVEN
        activity1 = UserActivity.objects.create(user=user)  # noqa
        activity2 = UserActivity.objects.create(user=user)  # noqa

        # WHEN
        activities = UserActivity.objects.filter(user=user).order_by("-login_time")

        # THEN
        assert activities.first().login_time >= activities.last().login_time
        assert activities.count() == 2

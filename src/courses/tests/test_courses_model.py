import pytest
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import CustomUser
from courses.models import MajorCategory, MinorCategory, Enrollment


@pytest.mark.django_db
class TestCoursesModels:
    """
    Courses 앱의 모델들을 테스트하는 클래스입니다.
    MajorCategory, MinorCategory, Enrollment 모델의 생성, 관계, 제약조건 등을 검증합니다.
    """

    @pytest.fixture
    def user(self):
        """테스트용 사용자를 생성하는 fixture입니다."""
        return CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",  # email 필드 추가
            password="testpass123",
        )

    @pytest.fixture
    def major_category(self):
        """테스트용 대분류(MajorCategory)를 생성하는 fixture입니다."""
        return MajorCategory.objects.create(name="Web Development", price=50000)

    @pytest.fixture
    def minor_category(self, major_category):
        """테스트용 소분류(MinorCategory)를 생성하는 fixture입니다."""
        return MinorCategory.objects.create(
            name="HTML/CSS",
            major_category=major_category,
            content="Learn the basics of HTML and CSS",
            order=1,
        )

    def test_major_category_creation(self, major_category):
        """
        MajorCategory 모델의 생성을 테스트합니다.
        생성된 객체의 속성값과 문자열 표현을 확인합니다.
        """
        assert major_category.name == "Web Development"
        assert major_category.price == 50000
        assert str(major_category) == "Web Development"

    def test_minor_category_creation(self, minor_category, major_category):
        """
        MinorCategory 모델의 생성을 테스트합니다.
        생성된 객체의 속성값, 관계, 문자열 표현을 확인합니다.
        """
        assert minor_category.name == "HTML/CSS"
        assert minor_category.major_category == major_category
        assert minor_category.content == "Learn the basics of HTML and CSS"
        assert minor_category.order == 1
        assert str(minor_category) == "Web Development - HTML/CSS"

    def test_minor_category_ordering(self, major_category):
        """
        MinorCategory 모델의 정렬 기능을 테스트합니다.
        'order' 필드에 따라 올바르게 정렬되는지 확인합니다.
        """
        MinorCategory.objects.create(
            name="HTML/CSS",
            major_category=major_category,
            content="Learn HTML/CSS",
            order=1,
        )
        MinorCategory.objects.create(
            name="JavaScript",
            major_category=major_category,
            content="Learn JS",
            order=2,
        )
        MinorCategory.objects.create(
            name="Python",
            major_category=major_category,
            content="Learn Python",
            order=3,
        )
        categories = MinorCategory.objects.all().order_by("order")
        assert categories[0].name == "HTML/CSS"
        assert categories[1].name == "JavaScript"
        assert categories[2].name == "Python"

    def test_enrollment_creation(self, user, major_category):
        """
        Enrollment 모델의 생성을 테스트합니다.
        생성된 객체의 속성값, 관계, 기본 상태, 문자열 표현을 확인합니다.
        """
        enrollment = Enrollment.objects.create(
            user=user,
            major_category=major_category,
            expiry_date=timezone.now() + timedelta(days=30),
        )
        assert enrollment.user == user
        assert enrollment.major_category == major_category
        assert enrollment.status == "active"
        assert str(enrollment) == "testuser - Web Development"

    def test_unique_enrollment(self, user, major_category):
        """
        Enrollment 모델의 유일성 제약조건을 테스트합니다.
        동일한 사용자가 같은 대분류에 중복 등록할 수 없음을 확인합니다.
        """
        Enrollment.objects.create(
            user=user,
            major_category=major_category,
            expiry_date=timezone.now() + timedelta(days=30),
        )
        with pytest.raises(ValidationError) as excinfo:
            enrollment = Enrollment(
                user=user,
                major_category=major_category,
                expiry_date=timezone.now() + timedelta(days=30),
            )
            enrollment.full_clean()

        assert "수강 신청의 사용자 또한 수강 대분류 은/는 이미 존재합니다." in str(
            excinfo.value
        )

    def test_enrollment_status_choices(self, user, major_category):
        """
        Enrollment 모델의 status 필드 선택 사항을 테스트합니다.
        유효한 상태값은 허용되고, 유효하지 않은 상태값은 거부되는지 확인합니다.
        """
        enrollment = Enrollment.objects.create(
            user=user,
            major_category=major_category,
            expiry_date=timezone.now() + timedelta(days=30),
            status="active",
        )
        assert enrollment.status == "active"

        enrollment.status = "completed"
        enrollment.save()
        assert enrollment.status == "completed"

        enrollment.status = "expired"
        enrollment.save()
        assert enrollment.status == "expired"

        with pytest.raises(ValidationError):
            enrollment.status = "invalid_status"
            enrollment.full_clean()

    def test_enrollment_expiry_date(self, user, major_category):
        """
        Enrollment 모델의 만료일 유효성을 테스트합니다.
        과거 날짜로 설정된 만료일은 유효성 검사에서 실패해야 합니다.
        """
        past_date = timezone.now() - timedelta(days=1)
        with pytest.raises(ValidationError):
            enrollment = Enrollment(
                user=user, major_category=major_category, expiry_date=past_date
            )
            enrollment.full_clean()

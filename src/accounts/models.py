from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    """
    Django의 AbstractUser를 확장한 사용자 정의 모델입니다.

    이 모델은 위니버시티 플랫폼에 특화된 추가 필드와 메서드를 포함합니다.
    """

    ROLES = (
        ("student", "학생"),
        ("admin", "관리자"),
    )
    GENDER_CHOICES = (
        ("M", "남성"),
        ("F", "여성"),
        ("O", "기타"),
        ("N", "밝히고 싶지 않음"),
    )
    role = models.CharField(
        max_length=10, choices=ROLES, default="student", verbose_name="역할"
    )
    nickname = models.CharField(max_length=50, blank=True, verbose_name="닉네임")
    total_study_time = models.DurationField(
        default=timezone.timedelta(), verbose_name="총 학습 시간"
    )
    subscription_end_date = models.DateTimeField(
        null=True, blank=True, verbose_name="구독 종료일"
    )

    # 새로 추가된 필드
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="성별"
    )
    phone_regex = RegexValidator(
        regex=r"^\d{3}-\d{3,4}-\d{4}$",
        message="전화번호는 '000-0000-0000' 형식으로 입력해주세요.",
    )
    contact_number = models.CharField(
        validators=[phone_regex], max_length=13, blank=True, verbose_name="연락처"
    )

    def is_subscription_active(self):
        """
        사용자의 구독이 현재 활성 상태인지 확인합니다.

        Returns:
            bool: 구독이 활성 상태이면 True, 그렇지 않으면 False를 반환합니다.
        """
        return (
            self.subscription_end_date and self.subscription_end_date > timezone.now()
        )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자들"


class UserActivity(models.Model):
    """
    사용자의 로그인 및 로그아웃 활동을 기록하는 모델입니다.

    이 모델은 사용자 참여도 추적과 보안 감사에 도움이 됩니다.
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="사용자",
    )
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="로그인 시간")
    logout_time = models.DateTimeField(
        null=True, blank=True, verbose_name="로그아웃 시간"
    )
    ip_address = models.GenericIPAddressField(verbose_name="IP 주소")

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

    class Meta:
        verbose_name = "사용자 활동"
        verbose_name_plural = "사용자 활동들"

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from .services import ProgressService


class MajorCategory(models.Model):
    """
    대분류 모델
    
    교육 과정의 대분류를 나타냅니다. 예를 들어 웹 개발, 데이터 분석 등 다양한 과정을 포함할 수 있습니다.
    """

    name = models.CharField(max_length=100, verbose_name="대분류명")
    price = models.PositiveIntegerField(verbose_name="강의가격", default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "대분류"
        verbose_name_plural = "대분류 목록"

    @property
    def progress_percent(self):
        """
        대분류의 학습 진행률을 계산하여 반환합니다.

        Returns:
            float: 대분류의 학습 진행률 (0 ~ 100).
        """
        return ProgressService.calculate_major_category_progress(self)


class MinorCategory(models.Model):
    """
    소분류 모델
    
    대분류에 속하는 세부 과목을 나타냅니다. 예를 들어 HTML/CSS, JavaScript, Python 등의 과목이 포함될 수 있습니다.
    """

    name = models.CharField(max_length=100, verbose_name="소분류명")
    major_category = models.ForeignKey(
        MajorCategory,
        on_delete=models.CASCADE,
        related_name="minor_categories",
        verbose_name="대분류",
    )
    content = models.TextField(verbose_name="내용")
    order = models.PositiveIntegerField(verbose_name="순서")

    class Meta:
        ordering = ["order"]
        verbose_name = "소분류"
        verbose_name_plural = "소분류 목록"

    def __str__(self):
        return f"{self.major_category.name} - {self.name}"

    @property
    def progress_percent(self):
        """
        소분류의 학습 진행률을 계산하여 반환합니다.

        Returns:
            float: 소분류의 학습 진행률 (0 ~ 100).
        """
        return ProgressService.calculate_category_progress(self)


class Enrollment(models.Model):
    """
    수강 신청 모델
    
    사용자가 특정 대분류 과정을 수강하는 정보를 저장합니다.
    """

    STATUS_CHOICES = [
        ("active", "진행중"),
        ("completed", "완료"),
        ("expired", "만료"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="사용자",
    )
    major_category = models.ForeignKey(
        MajorCategory,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="수강 대분류",
        null=True,
    )
    enrollment_date = models.DateTimeField(
        auto_now_add=True, verbose_name="수강 신청일"
    )
    expiry_date = models.DateTimeField(verbose_name="수강 만료일")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active", verbose_name="상태"
    )

    def clean(self):
        """
        수강 신청의 유효성을 검증합니다.

        만료일은 현재 시점 이후여야 하며, 수강 신청일보다 만료일이 늦어야 하고,
        수강 기간은 최대 2년을 넘지 않아야 합니다.

        Raises:
            ValidationError: 유효성 검증 실패 시 예외를 발생시킵니다.
        """
        now = timezone.now()

        if not self.enrollment_date:
            self.enrollment_date = now

        if self.expiry_date and self.expiry_date.tzinfo is None:
            self.expiry_date = timezone.make_aware(self.expiry_date)

        if self.expiry_date and self.expiry_date < now:
            raise ValidationError("수강 만료일은 현재 시간 이후여야 합니다.")

        if self.expiry_date and self.enrollment_date and self.expiry_date < self.enrollment_date:
            raise ValidationError("수강 만료일은 수강 신청일 이후여야 합니다.")

        max_duration = timezone.timedelta(days=365 * 2)
        if self.expiry_date and self.enrollment_date and (self.expiry_date - self.enrollment_date) > max_duration:
            raise ValidationError("수강 기간은 2년을 초과할 수 없습니다.")

    def save(self, *args, **kwargs):
        """
        수강 신청을 저장하기 전에 데이터 유효성을 검사합니다.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.major_category.name}"

    class Meta:
        verbose_name = "수강 신청"
        verbose_name_plural = "수강 신청 목록"
        unique_together = ["user", "major_category"]  # 사용자와 대분류는 중복될 수 없음

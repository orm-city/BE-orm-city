from django.db import models
from accounts.models import CustomUser
from .services import ProgressService


class MajorCategory(models.Model):
    """
    대분류 모델

    이 모델은 교육 과정의 대분류를 나타냅니다.
    예: 웹 개발, 데이터 분석 등
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
        return ProgressService.calculate_major_category_progress(self)


class MinorCategory(models.Model):
    """
    소분류 모델

    이 모델은 대분류에 속한 세부 과목을 나타냅니다.
    예: HTML/CSS, JavaScript, Python 등
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
        return ProgressService.calculate_category_progress(self)


class Enrollment(models.Model):
    """
    수강 신청 모델 (MajorCategory 기반)

    이 모델은 사용자의 대분류(MajorCategory) 과목 수강 신청 정보를 나타냅니다.
    """

    STATUS_CHOICES = [
        ("active", "진행중"),
        ("completed", "완료"),
        ("expired", "만료"),
    ]
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="사용자",
    )
    major_category = models.ForeignKey(
        MajorCategory,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="수강 대분류",
    )
    enrollment_date = models.DateTimeField(
        auto_now_add=True, verbose_name="수강 신청일"
    )
    expiry_date = models.DateTimeField(verbose_name="수강 만료일")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active", verbose_name="상태"
    )

    def __str__(self):
        return f"{self.user.username} - {self.major_category.name}"

    class Meta:
        verbose_name = "수강 신청"
        verbose_name_plural = "수강 신청 목록"
        unique_together = ["user", "major_category"]

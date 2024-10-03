from django.conf import settings
from django.db import models
from courses.models import MajorCategory, Enrollment
from django.utils import timezone


class Payment(models.Model):
    """
    결제 모델 정의
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="사용자",
    )
    major_category = models.ForeignKey(
        MajorCategory,
        on_delete=models.CASCADE,
        null=True,
        related_name="payments",
        verbose_name="수강 대분류",
    )
    total_amount = models.PositiveIntegerField(verbose_name="결제 금액")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="결제일")
    receipt_url = models.URLField(null=True, blank=True, verbose_name="영수증 URL")
    merchant_uid = models.CharField(
        max_length=100, unique=True, null=True, verbose_name="주문번호"
    )
    imp_uid = models.CharField(
        max_length=100, unique=True, null=True, verbose_name="아임포트 거래 고유번호"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("ready", "미결제"),
            ("paid", "결제완료"),
            ("cancelled", "결제취소"),
            ("failed", "결제실패"),
        ],
        default="ready",
        verbose_name="결제 상태",
    )
    refund_status = models.CharField(
        max_length=20,
        choices=[
            ("NOT_REQUESTED", "요청 없음"),
            ("REQUESTED", "환불 요청됨"),
            ("COMPLETED", "환불 완료"),
            ("FAILED", "환불 실패"),
        ],
        default="NOT_REQUESTED",
        verbose_name="환불 상태",
    )

    ENROLLMENT_DURATION = timezone.timedelta(days=365 * 2)

    def create_enrollment(self):
        if self.payment_status == "paid" and not hasattr(self, "enrollment"):
            try:
                enrollment = Enrollment.objects.create(
                    user=self.user,
                    major_category=self.major_category,
                    enrollment_date=self.payment_date,
                    expiry_date=self.payment_date + self.ENROLLMENT_DURATION,
                    status="active",
                )
                return enrollment
            except Exception as e:
                # 로그 기록 또는 에러 처리
                print(f"Enrollment creation failed: {str(e)}")
        return None

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.payment_status == "paid":
            enrollment = self.create_enrollment()
            if enrollment:
                # 생성된 enrollment를 payment와 연결 (선택적)
                self.enrollment = enrollment
                super().save(update_fields=["enrollment"])

    class Meta:
        verbose_name = "결제"
        verbose_name_plural = "결제 목록"

    def __str__(self):
        return f"{self.user.username}의 {self.major_category.name} 결제"

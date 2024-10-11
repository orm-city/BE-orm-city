from django.conf import settings
from django.db import models
from courses.models import MajorCategory, Enrollment
from django.utils import timezone


class Payment(models.Model):
    """
    결제 모델 정의

    이 모델은 사용자의 결제 내역을 저장합니다. 결제 상태, 환불 정보, 관련된 수강 등록 정보 등을 포함합니다.
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
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment",
        verbose_name="등록 정보",
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
    refund_amount = models.PositiveIntegerField(
        verbose_name="환불 금액", default=0, help_text="환불된 총 금액"
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
    refund_deadline = models.DateTimeField(
        verbose_name="환불 가능 기한", null=True, blank=True
    )

    ENROLLMENT_DURATION = timezone.timedelta(days=365 * 2)
    DEFAULT_REFUND_PERIOD = timezone.timedelta(days=7)

    def save(self, *args, **kwargs):
        """
        결제를 저장할 때 환불 가능 기한을 설정합니다.
        """
        if not self.refund_deadline and self.payment_date:
            self.refund_deadline = self.payment_date + self.DEFAULT_REFUND_PERIOD
        super().save(*args, **kwargs)

    def is_refundable(self):
        """
        환불 가능 여부를 반환합니다. 현재 시간이 환불 가능 기한 내인지 확인합니다.
        """
        return timezone.now() <= self.refund_deadline

    def create_enrollment(self):
        """
        결제가 완료되면 수강 등록을 생성합니다.
        """
        if self.payment_status == "paid" and not self.enrollment:
            try:
                enrollment, created = Enrollment.objects.get_or_create(
                    user=self.user,
                    major_category=self.major_category,
                    defaults={
                        "enrollment_date": self.payment_date,
                        "expiry_date": self.payment_date + self.ENROLLMENT_DURATION,
                        "status": "active",
                    },
                )
                self.enrollment = enrollment
                return enrollment
            except Exception as e:
                # 로그 기록 또는 에러 처리
                print(f"Enrollment creation failed: {str(e)}")
        return None

    class Meta:
        verbose_name = "결제"
        verbose_name_plural = "결제 목록"

    def __str__(self):
        return f"{self.user.username}의 {self.major_category.name} 결제"

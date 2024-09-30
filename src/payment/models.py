from django.conf import settings
from django.db import models
from courses.models import MajorCategory


class Payment(models.Model):
    """
    결제 모델 정의
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    major_category = models.ForeignKey(
        MajorCategory, on_delete=models.CASCADE, null=True, related_name="payments"
    )
    total_amount = models.PositiveIntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    receipt_url = models.URLField(null=True, blank=True)
    merchant_uid = models.CharField(
        max_length=100, unique=True, null=True
    )  # 아임포트 결제 고유 아이디
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("ready", "미결제"),
            ("paid", "결제완료"),
            ("cancelled", "결제취소"),
            ("failed", "결제실패"),
        ],
        default="PENDING",
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
    )

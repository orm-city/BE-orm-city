from django.conf import settings
from django.db import models
from courses.models import MajorCategory


class Payment(models.Model):
    # 결제 상태
    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "결제대기"),
        ("COMPLETED", "결제완료"),
        ("FAILED", "결제실패"),
        ("CANCELLED", "결제취소"),
    ]
    # 환불 상태
    REFUND_STATUS_CHOICES = [
        ("NOT_REQUESTED", "요청없음"),
        ("REQUESTED", "요청됨"),
        ("COMPLETED", "요청완료"),
        ("FAILED", "요청실패"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    major_category = models.ForeignKey(
        MajorCategory, on_delete=models.CASCADE, null=True, related_name="payments"
    )
    total_amount = models.PositiveIntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    receipt_url = models.URLField(null=True, blank=True)
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="PENDING"
    )

    refund_status = models.CharField(
        max_length=20, choices=REFUND_STATUS_CHOICES, default="NOT_REQUESTED"
    )

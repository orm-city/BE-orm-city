from django.conf import settings
from django.db import models


class Payment(models.Model):
    # 결제 상태
    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]
    # 환불 상태
    REFUND_STATUS_CHOICES = [
        ("NOT_REQUESTED", "Not Requested"),
        ("REQUESTED", "Requested"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    # course 외래키

    amount = models.PositiveIntegerField()

    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="PENDING"
    )

    refund_status = models.CharField(
        max_length=20, choices=REFUND_STATUS_CHOICES, default="NOT_REQUESTED"
    )

    receipt_url = models.URLField(null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

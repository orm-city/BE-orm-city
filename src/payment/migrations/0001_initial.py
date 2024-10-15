# Generated by Django 5.1.2 on 2024-10-13 16:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("courses", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_amount", models.PositiveIntegerField(verbose_name="결제 금액")),
                (
                    "payment_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="결제일"),
                ),
                (
                    "receipt_url",
                    models.URLField(blank=True, null=True, verbose_name="영수증 URL"),
                ),
                (
                    "merchant_uid",
                    models.CharField(
                        max_length=100, null=True, unique=True, verbose_name="주문번호"
                    ),
                ),
                (
                    "imp_uid",
                    models.CharField(
                        max_length=100,
                        null=True,
                        unique=True,
                        verbose_name="아임포트 거래 고유번호",
                    ),
                ),
                (
                    "refund_amount",
                    models.PositiveIntegerField(
                        default=0, help_text="환불된 총 금액", verbose_name="환불 금액"
                    ),
                ),
                (
                    "payment_status",
                    models.CharField(
                        choices=[
                            ("ready", "미결제"),
                            ("paid", "결제완료"),
                            ("cancelled", "결제취소"),
                            ("failed", "결제실패"),
                        ],
                        default="ready",
                        max_length=20,
                        verbose_name="결제 상태",
                    ),
                ),
                (
                    "refund_status",
                    models.CharField(
                        choices=[
                            ("NOT_REQUESTED", "요청 없음"),
                            ("REQUESTED", "환불 요청됨"),
                            ("COMPLETED", "환불 완료"),
                            ("FAILED", "환불 실패"),
                        ],
                        default="NOT_REQUESTED",
                        max_length=20,
                        verbose_name="환불 상태",
                    ),
                ),
                (
                    "refund_deadline",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="환불 가능 기한"
                    ),
                ),
                (
                    "enrollment",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payments",
                        to="courses.enrollment",
                        verbose_name="등록 정보",
                    ),
                ),
                (
                    "major_category",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="courses.majorcategory",
                        verbose_name="수강 대분류",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "결제",
                "verbose_name_plural": "결제 목록",
            },
        ),
    ]

# Generated by Django 5.1.2 on 2024-10-13 16:07

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("courses", "0001_initial"),
        ("payment", "0001_initial"),
        ("progress", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyVisit",
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
                ("date", models.DateField(unique=True, verbose_name="방문 날짜")),
                (
                    "student_unique_visitors",
                    models.IntegerField(default=0, verbose_name="학생 고유 방문자 수"),
                ),
                (
                    "student_total_views",
                    models.IntegerField(default=0, verbose_name="학생 총 조회 수"),
                ),
                (
                    "unique_ips",
                    models.TextField(default="[]", verbose_name="고유 IP 목록"),
                ),
            ],
            options={
                "verbose_name": "일일 학생 방문",
                "verbose_name_plural": "일일 학생 방문 목록",
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="DailyPayment",
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
                ("date", models.DateField(verbose_name="결제일")),
                (
                    "payment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_payments",
                        to="payment.payment",
                        verbose_name="결제 정보",
                    ),
                ),
            ],
            options={
                "verbose_name": "일별 결제",
                "verbose_name_plural": "일별 결제 목록",
            },
        ),
        migrations.CreateModel(
            name="UserVideoProgress",
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
                ("date", models.DateField(verbose_name="날짜")),
                (
                    "daily_watch_duration",
                    models.IntegerField(
                        default=0, verbose_name="일일 시청 시간(초 단위)"
                    ),
                ),
                (
                    "progress_percent",
                    models.FloatField(default=0, verbose_name="진행률"),
                ),
                (
                    "user_progress",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="video_progresses",
                        to="progress.userprogress",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExpirationNotification",
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
                ("notification_date", models.DateField(verbose_name="알림 예정일")),
                (
                    "is_sent",
                    models.BooleanField(default=False, verbose_name="발송 여부"),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expiration_notifications",
                        to="courses.enrollment",
                        verbose_name="수강 등록",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expiration_notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "수강 만료 알림",
                "verbose_name_plural": "수강 만료 알림 목록",
                "unique_together": {("enrollment", "notification_date")},
            },
        ),
        migrations.CreateModel(
            name="UserLearningRecord",
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
                (
                    "date",
                    models.DateField(
                        default=django.utils.timezone.now, verbose_name="날짜"
                    ),
                ),
                (
                    "major_category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learning_records",
                        to="courses.majorcategory",
                        verbose_name="대분류",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learning_records",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
                (
                    "user_activity",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="learning_records",
                        to="accounts.useractivity",
                        verbose_name="사용자 활동",
                    ),
                ),
            ],
            options={
                "verbose_name": "사용자 학습 기록",
                "verbose_name_plural": "사용자 학습 기록 목록",
                "unique_together": {("user", "date", "major_category")},
            },
        ),
    ]

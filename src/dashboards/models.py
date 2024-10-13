import json
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from accounts.models import UserActivity
from courses.models import MajorCategory, Enrollment
from payment.models import Payment
from progress.models import UserProgress


class DailyVisit(models.Model):
    """
    일일 방문 기록 모델

    학생들의 일일 방문자 수와 총 조회 수, 그리고 고유 IP 목록을 저장합니다.
    """

    date = models.DateField(unique=True, verbose_name="방문 날짜")
    student_unique_visitors = models.IntegerField(
        default=0, verbose_name="학생 고유 방문자 수"
    )
    student_total_views = models.IntegerField(default=0, verbose_name="학생 총 조회 수")
    unique_ips = models.TextField(default="[]", verbose_name="고유 IP 목록")

    def set_unique_ips(self, ips):
        """
        고유한 IP 목록을 설정합니다.
        """
        self.unique_ips = json.dumps(list(set(ips)))

    def get_unique_ips(self):
        """
        저장된 고유 IP 목록을 반환합니다.
        """
        return json.loads(self.unique_ips)

    class Meta:
        ordering = ["-date"]  # 최신 날짜가 먼저 오도록 정렬
        verbose_name = "일일 학생 방문"
        verbose_name_plural = "일일 학생 방문 목록"

    def __str__(self):
        return f"{self.date} 학생 방문: {self.student_unique_visitors}명 고유 방문, {self.student_total_views}회 조회"


class DailyPayment(models.Model):
    """
    일별 결제 기록 모델

    특정 날짜에 발생한 결제 정보를 저장합니다.
    """

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="daily_payments",
        verbose_name="결제 정보",
    )
    date = models.DateField(verbose_name="결제일")

    def __str__(self):
        return (
            f"{self.date}의 결제: {self.payment.user}님, {self.payment.major_category}"
        )

    class Meta:
        verbose_name = "일별 결제"
        verbose_name_plural = "일별 결제 목록"

    @property
    def user(self):
        return self.payment.user

    @property
    def major_category(self):
        return self.payment.major_category

    @property
    def amount(self):
        return self.payment.total_amount


class UserLearningRecord(models.Model):
    """
    사용자 학습 기록 모델

    사용자가 특정 날짜에 학습한 기록을 저장합니다.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="사용자",
        related_name="learning_records",
    )
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    user_activity = models.ForeignKey(
        UserActivity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="사용자 활동",
        related_name="learning_records",
    )
    major_category = models.ForeignKey(
        MajorCategory,
        on_delete=models.CASCADE,
        verbose_name="대분류",
        related_name="learning_records",
    )

    class Meta:
        verbose_name = "사용자 학습 기록"
        verbose_name_plural = "사용자 학습 기록 목록"
        unique_together = ["user", "date", "major_category"]

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @property
    def login_time(self):
        return self.user_activity.login_time if self.user_activity else None

    @property
    def logout_time(self):
        return self.user_activity.logout_time if self.user_activity else None

    def total_study_time(self):
        """
        학습 기록에서 총 학습 시간을 계산합니다.
        """
        return timedelta(seconds=self.total_study_seconds)


class UserVideoProgress(models.Model):
    """
    사용자 비디오 학습 진행 모델

    사용자의 하루 동안의 비디오 학습 시간을 기록합니다.
    """

    user_progress = models.ForeignKey(
        UserProgress, on_delete=models.CASCADE, related_name="video_progresses"
    )
    date = models.DateField(verbose_name="날짜")
    daily_watch_duration = models.IntegerField(
        default=0, verbose_name="일일 시청 시간(초 단위)"
    )
    progress_percent = models.FloatField(default=0, verbose_name="진행률")

    def formatted_watch_duration(self):
        """
        시청 시간을 형식화하여 반환합니다.
        """
        return str(timedelta(seconds=self.daily_watch_duration))

    def __str__(self):
        return f"{self.user_progress.user.username} - {self.date}"


class ExpirationNotification(models.Model):
    """
    수강 만료 알림 모델

    특정 수강 등록에 대한 만료 알림 정보를 저장합니다.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="사용자",
        related_name="expiration_notifications",
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        verbose_name="수강 등록",
        related_name="expiration_notifications",
    )
    notification_date = models.DateField(verbose_name="알림 예정일")
    is_sent = models.BooleanField(default=False, verbose_name="발송 여부")

    class Meta:
        verbose_name = "수강 만료 알림"
        verbose_name_plural = "수강 만료 알림 목록"
        unique_together = ["enrollment", "notification_date"]

    def __str__(self):
        return f"{self.user.username}의 {self.enrollment.major_category.name} 수강 만료 알림 ({self.notification_date})"

    @property
    def days_until_expiry(self):
        """
        수강 만료일까지 남은 일수를 계산하여 반환합니다.
        """
        return (self.enrollment.expiry_date - self.notification_date).days

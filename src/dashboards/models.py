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
    일일 방문 기록 모델.

    학생들의 일일 고유 방문자 수, 총 조회 수 및 고유 IP 목록을 저장합니다.

    Attributes:
        date (DateField): 방문 날짜.
        student_unique_visitors (IntegerField): 고유 방문자 수.
        student_total_views (IntegerField): 총 조회 수.
        unique_ips (TextField): 고유 IP 목록을 저장하는 필드.
    """

    date = models.DateField(unique=True, verbose_name="방문 날짜")
    student_unique_visitors = models.IntegerField(
        default=0, verbose_name="학생 고유 방문자 수"
    )
    student_total_views = models.IntegerField(default=0, verbose_name="학생 총 조회 수")
    unique_ips = models.TextField(default="[]", verbose_name="고유 IP 목록")

    def set_unique_ips(self, ips):
        """
        고유 IP 목록을 설정합니다.

        Args:
            ips (list): 새로운 고유 IP 목록.
        """
        self.unique_ips = json.dumps(list(set(ips)))

    def get_unique_ips(self):
        """
        저장된 고유 IP 목록을 반환합니다.

        Returns:
            list: IP 목록.
        """
        return json.loads(self.unique_ips)

    class Meta:
        ordering = ["-date"]
        verbose_name = "일일 학생 방문"
        verbose_name_plural = "일일 학생 방문 목록"

    def __str__(self):
        return f"{self.date} 학생 방문: {self.student_unique_visitors}명 고유 방문, {self.student_total_views}회 조회"


class DailyPayment(models.Model):
    """
    일별 결제 기록 모델.

    특정 날짜에 발생한 결제 정보를 저장합니다.

    Attributes:
        payment (ForeignKey): 결제 정보.
        date (DateField): 결제일.
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
        """
        결제와 관련된 사용자를 반환합니다.

        Returns:
            User: 결제와 연결된 사용자.
        """
        return self.payment.user

    @property
    def major_category(self):
        """
        결제와 관련된 대분류를 반환합니다.

        Returns:
            MajorCategory: 결제와 연결된 대분류.
        """
        return self.payment.major_category

    @property
    def amount(self):
        """
        결제 금액을 반환합니다.

        Returns:
            float: 결제 금액.
        """
        return self.payment.total_amount


class UserLearningRecord(models.Model):
    """
    사용자 학습 기록 모델.

    사용자가 특정 날짜에 학습한 기록을 저장합니다.

    Attributes:
        user (ForeignKey): 사용자.
        date (DateField): 학습 기록 날짜.
        user_activity (ForeignKey): 사용자 활동과의 연관성.
        major_category (ForeignKey): 학습한 대분류.
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
        """
        사용자의 로그인 시간을 반환합니다.

        Returns:
            datetime: 로그인 시간.
        """
        return self.user_activity.login_time if self.user_activity else None

    @property
    def logout_time(self):
        """
        사용자의 로그아웃 시간을 반환합니다.

        Returns:
            datetime: 로그아웃 시간.
        """
        return self.user_activity.logout_time if self.user_activity else None

    def total_study_time(self):
        """
        학습 기록에서 총 학습 시간을 계산합니다.

        Returns:
            timedelta: 학습에 소요된 총 시간.
        """
        return timedelta(seconds=self.total_study_seconds)


class UserVideoProgress(models.Model):
    """
    사용자 비디오 학습 진행 모델.

    사용자의 하루 동안의 비디오 학습 시간을 기록합니다.

    Attributes:
        user_progress (ForeignKey): 사용자 진행 기록과 연관된 필드.
        date (DateField): 학습 날짜.
        daily_watch_duration (IntegerField): 하루 동안 시청한 시간 (초).
        progress_percent (FloatField): 학습 진행률.
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

        Returns:
            str: 형식화된 시청 시간.
        """
        return str(timedelta(seconds=self.daily_watch_duration))

    def __str__(self):
        return f"{self.user_progress.user.username} - {self.date}"


class ExpirationNotification(models.Model):
    """
    수강 만료 알림 모델.

    특정 수강 등록에 대한 만료 알림 정보를 저장합니다.

    Attributes:
        user (ForeignKey): 사용자.
        enrollment (ForeignKey): 수강 등록 정보.
        notification_date (DateField): 알림 예정일.
        is_sent (BooleanField): 알림 발송 여부.
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

        Returns:
            int: 남은 일수.
        """
        return (self.enrollment.expiry_date - self.notification_date).days

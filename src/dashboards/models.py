from django.db import models
from accounts.models import CustomUser, UserActivity
from courses.models import MajorCategory, Enrollment
from payment.models import Payment
from django.utils import timezone
from progress.models import UserProgress


class DailyVisit(models.Model):
    date = models.DateField(unique=True, verbose_name="날짜")
    student_unique_visitors = models.IntegerField(
        default=0, verbose_name="학생 고유 방문자 수"
    )
    student_total_views = models.IntegerField(default=0, verbose_name="학생 총 조회수")

    def __str__(self):
        return f"{self.date} 학생 방문: {self.student_unique_visitors}명 고유 방문, {self.student_total_views}회 조회"

    class Meta:
        verbose_name = "일일 학생 방문"
        verbose_name_plural = "일일 학생 방문 목록"


class DailyPayment(models.Model):
    date = models.DateField(verbose_name="결제일")
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, verbose_name="결제 정보"
    )

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
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="사용자"
    )
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    user_activity = models.ForeignKey(
        UserActivity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="사용자 활동",
    )
    major_category = models.ForeignKey(
        MajorCategory, on_delete=models.CASCADE, verbose_name="대분류"
    )

    class Meta:
        verbose_name = "사용자 학습 기록"
        verbose_name_plural = "사용자 학습 기록 목록"
        unique_together = ["user", "date", "major_category"]

    def __str__(self):
        return f"{self.user}의 {self.date} {self.major_category} 학습 기록"

    @property
    def login_time(self):
        return self.user_activity.login_time if self.user_activity else None

    @property
    def logout_time(self):
        return self.user_activity.logout_time if self.user_activity else None

    @property
    def total_study_time(self):
        # 이 로직은 views나 services에서 구현해야 합니다.
        pass

    @property
    def progress_percent(self):
        # 이 로직은 views나 services에서 구현해야 합니다.
        pass


class UserVideoProgress(models.Model):
    user_progress = models.ForeignKey(
        UserProgress,
        on_delete=models.CASCADE,
        related_name="daily_records",
        verbose_name="사용자 진행 상황",
    )
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    daily_watch_duration = models.DurationField(
        default=timezone.timedelta, verbose_name="일일 시청 시간"
    )

    class Meta:
        verbose_name = "사용자 일일 비디오 진행 상황"
        verbose_name_plural = "사용자 일일 비디오 진행 상황 목록"
        unique_together = ["user_progress", "date"]

    def __str__(self):
        return f"{self.user_progress.user}의 {self.user_progress.video} 진행 상황 ({self.date})"

    @property
    def user(self):
        return self.user_progress.user

    @property
    def video(self):
        return self.user_progress.video

    @property
    def total_watch_duration(self):
        return self.user_progress.time_spent

    @property
    def progress_percent(self):
        return self.user_progress.progress_percent

    def update_daily_watch_duration(self, duration):
        self.daily_watch_duration += duration
        self.save()


# 현재 미션은 완성이 아니기에 일단 미구현
# class UserMissionProgress(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
#     is_passed = models.BooleanField(default=False)
#     completed_date = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.user}'s progress on {self.mission}"


class ExpirationNotification(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="사용자"
    )
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, verbose_name="수강 등록"
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
        return (self.enrollment.expiry_date - self.notification_date).days

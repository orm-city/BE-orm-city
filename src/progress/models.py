from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError

from courses.models import Enrollment
from videos.models import Video


class UserProgress(models.Model):
    """
    유저 수강 진행 모델
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progresses",
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="progresses"
    )
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="progresses"
    )
    is_completed = models.BooleanField(default=False, verbose_name="수강 완료 여부")
    last_accessed = models.DateTimeField(
        default=timezone.now, verbose_name="마지막 접속 시간"
    )
    progress_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="수강 진행률(%)",
    )
    time_spent = models.DurationField(
        default=timezone.timedelta, verbose_name="수강 진행 시간"
    )
    last_position = models.PositiveIntegerField(
        default=0, verbose_name="마지막 시청 위치(초단위)"
    )

    def __str__(self):
        return f"수강생:{self.user.username}, 강의:{self.video.name}, 수강률:({self.progress_percent}%)"

    def update_progress(self, additional_time, last_position):
        # 입력값 검증
        if last_position < 0:
            raise ValidationError("last_position must be non-negative")

        if additional_time < timezone.timedelta(0):
            raise ValidationError("additional_time must be non-negative")

        # Video 총 길이 가져오기
        video_duration = self.video.duration.total_seconds()

        # last_position 제한
        self.last_position = min(int(last_position), int(video_duration))

        # progress_percent 계산
        self.progress_percent = min(
            100, int((self.last_position / video_duration) * 100)
        )

        # time_spent 업데이트 및 제한
        self.time_spent += additional_time
        if self.time_spent > self.video.duration:
            self.time_spent = self.video.duration

        # 마지막 접근 시간 업데이트
        self.last_accessed = timezone.now()

        # 완료 여부 확인
        self.is_completed = self.progress_percent == 100

        self.save()

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

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
    is_completed = models.BooleanField(default=False)  # 수강 완료 여부
    last_accessed = models.DateTimeField(default=timezone.now)  # 마지막 접근 시간
    progress_percent = models.IntegerField(  # 진행률
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    time_spent = models.DurationField(default=timezone.timedelta)  # 수강 진행 시간
    last_position = models.PositiveIntegerField(default=0)  # 마지막 시청 위치 (초 단위)

    def __str__(self):
        return f"수강생:{self.user.username}, 강의:{self.video.name}, 수강률:({self.progress_percent}%)"

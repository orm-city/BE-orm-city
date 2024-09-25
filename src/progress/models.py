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

    def __str__(self):
        return f"수강생:{self.user.username}, 강의:{self.video.name}, 수강률:({self.progress_percent}%)"

    def update_progress(self, new_percent, additional_time):
        self.progress_percent = min(100, max(0, new_percent))
        self.time_spent += additional_time
        self.last_accessed = timezone.now()
        if self.progress_percent == 100:
            self.is_completed = True
        self.save()

    def reset_progress(self):
        self.is_completed = False
        self.progress_percent = 0
        self.time_spent = timezone.timedelta()
        self.save()

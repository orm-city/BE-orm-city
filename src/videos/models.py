from django.db import models

from courses.models import MinorCategory


class Video(models.Model):
    """
    Video에 대한 모델 정의
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    video_url = models.URLField()
    minor_category = models.ForeignKey(
        MinorCategory,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name="소분류",
    )
    duration = models.DurationField()  # 동영상의 길이
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

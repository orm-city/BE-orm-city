from django.db import models


class Video(models.Model):
    """
    Video에 대한 모델 정의
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    video_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

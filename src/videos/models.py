from django.db import models

from courses.models import MinorCategory


class Video(models.Model):
    """
    Video 모델 정의

    이 모델은 소분류 카테고리와 연결된 동영상에 대한 정보를 저장합니다.

    Attributes:
        name (str): 동영상의 제목.
        description (str): 동영상 설명.
        video_url (URLField): 동영상 URL.
        minor_category (ForeignKey): 해당 동영상이 속한 소분류 카테고리.
        duration (DurationField): 동영상의 길이.
        order (PositiveIntegerField): 동영상의 순서.
        created_at (DateTimeField): 동영상이 생성된 날짜와 시간.
    """

    name = models.CharField(max_length=100, verbose_name="동영상 제목")
    description = models.TextField(verbose_name="동영상 설명")
    video_url = models.URLField(verbose_name="동영상 URL")
    minor_category = models.ForeignKey(
        MinorCategory,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name="소분류 카테고리",
    )
    duration = models.DurationField(verbose_name="동영상 길이")  # 동영상의 길이
    order = models.PositiveIntegerField(default=0, verbose_name="동영상 순서")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")

    def __str__(self):
        """
        동영상의 이름을 반환합니다.
        
        Returns:
            str: 동영상의 제목.
        """
        return self.name

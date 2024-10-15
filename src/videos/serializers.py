from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """
    비디오 정보를 직렬화하는 Serializer 클래스.

    Attributes:
        model (Model): 직렬화할 모델.
        fields (tuple): 직렬화할 필드들.
    """
    
    class Meta:
        model = Video
        fields = (
            "id",
            "name",
            "description",
            "video_url",
            "minor_category",
            "duration",
            "order",
            "created_at",
        )


class ProgressUpdateSerializer(serializers.Serializer):
    """
    학습 진행 업데이트를 위한 Serializer 클래스.

    Attributes:
        video_id (int): 비디오 ID.
        progress_percent (int): 학습 진행률 (0~100%).
        time_spent (int): 학습에 소요된 시간 (초 단위).
        last_position (int): 마지막 학습 위치 (초 단위).
    """
    
    video_id = serializers.IntegerField()
    progress_percent = serializers.IntegerField(min_value=0, max_value=100)
    time_spent = serializers.IntegerField(min_value=0)
    last_position = serializers.IntegerField(min_value=0)

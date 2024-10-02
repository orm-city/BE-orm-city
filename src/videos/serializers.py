from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
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

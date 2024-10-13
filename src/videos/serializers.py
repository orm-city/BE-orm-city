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


class ProgressUpdateSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    progress_percent = serializers.IntegerField(min_value=0, max_value=100)
    time_spent = serializers.IntegerField(min_value=0)
    last_position = serializers.IntegerField(min_value=0)

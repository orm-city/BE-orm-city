from rest_framework import serializers

from .models import UserProgress
from courses.models import MajorCategory


class UserProgressSerializer(serializers.ModelSerializer):
    video_name = serializers.CharField(source="video.name", read_only=True)

    class Meta:
        model = UserProgress
        fields = [
            "id",
            "user",
            "video",
            "video_name",
            "enrollment",
            "is_completed",
            "last_accessed",
            "progress_percent",
            "time_spent",
            "last_position",
        ]
        read_only_fields = [
            "user",
            "video",
            "enrollment",
            "is_completed",
            "progress_percent",
        ]


class UserProgressUpdateSerializer(serializers.ModelSerializer):
    additional_time = serializers.DurationField(write_only=True)
    last_position = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserProgress
        fields = ["additional_time", "last_position"]


class CategoryProgressSerializer(serializers.ModelSerializer):
    progress_percent = serializers.FloatField()

    class Meta:
        model = MajorCategory
        fields = ["id", "name", "progress_percent"]


class OverallProgressSerializer(serializers.Serializer):
    overall_progress = serializers.FloatField()
    category_progress = CategoryProgressSerializer(many=True)


class VideoProgressSerializer(serializers.ModelSerializer):
    video_name = serializers.CharField(source="video.name", read_only=True)

    class Meta:
        model = UserProgress
        fields = [
            "id",
            "video",
            "video_name",
            "is_completed",
            "progress_percent",
            "time_spent",
            "last_position",
        ]
        read_only_fields = [
            "id",
            "video",
            "video_name",
            "is_completed",
            "progress_percent",
        ]

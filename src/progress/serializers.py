from rest_framework import serializers

from .models import UserProgress
from courses.models import MajorCategory


class UserProgressSerializer(serializers.ModelSerializer):
    """
    UserProgress 객체를 직렬화하는 Serializer.

    추가 필드:
    - video_name: 관련 비디오의 이름.
    """

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
    """
    유저의 수강 진행률을 업데이트하는 Serializer.

    필드:
    - additional_time: 추가된 시청 시간.
    - last_position: 마지막 시청 위치.
    """

    additional_time = serializers.DurationField(write_only=True)
    last_position = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserProgress
        fields = ["additional_time", "last_position"]


class CategoryProgressSerializer(serializers.ModelSerializer):
    """
    MajorCategory의 수강 진행률을 직렬화하는 Serializer.

    필드:
    - progress_percent: 해당 카테고리의 진행률.
    """

    progress_percent = serializers.FloatField()

    class Meta:
        model = MajorCategory
        fields = ["id", "name", "progress_percent"]


class OverallProgressSerializer(serializers.Serializer):
    """
    유저의 전체 수강 진행률을 직렬화하는 Serializer.

    필드:
    - overall_progress: 전체 진행률.
    - category_progress: 카테고리별 진행률 목록.
    """

    overall_progress = serializers.FloatField()
    category_progress = CategoryProgressSerializer(many=True)


class VideoProgressSerializer(serializers.ModelSerializer):
    """
    유저의 비디오 수강 진행률을 직렬화하는 Serializer.

    필드:
    - video_name: 비디오의 이름.
    """

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

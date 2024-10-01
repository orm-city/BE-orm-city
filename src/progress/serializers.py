from rest_framework import serializers
from .models import UserProgress
from videos.serializers import VideoSerializer
from courses.serializers import EnrollmentSerializer


class UserProgressSerializer(serializers.ModelSerializer):
    """
    사용자의 학습 진행 상황을 직렬화하는 시리얼라이저.
    비디오와 수강 정보를 포함하여 상세한 진행 상황을 제공합니다.
    """

    video = VideoSerializer(read_only=True)
    enrollment = EnrollmentSerializer(read_only=True)

    class Meta:
        model = UserProgress
        fields = [
            "id",
            "video",
            "enrollment",
            "is_completed",
            "last_accessed",
            "progress_percent",
            "time_spent",
            "last_position",
        ]
        read_only_fields = [
            "id",
            "video",
            "enrollment",
            "is_completed",
            "last_accessed",
        ]


class UserProgressUpdateSerializer(serializers.Serializer):
    """
    사용자의 학습 진행 상황 업데이트를 위한 시리얼라이저.
    클라이언트로부터 받은 데이터의 유효성을 검사합니다.
    """

    progress_percent = serializers.IntegerField(min_value=0, max_value=100)
    additional_time = serializers.IntegerField(min_value=0)  # 초 단위
    last_position = serializers.IntegerField(min_value=0)


class UserOverallProgressSerializer(serializers.Serializer):
    """
    사용자의 전체 학습 진행 상황 요약을 직렬화하는 시리얼라이저.
    총 비디오 수, 완료된 비디오 수, 전체 진행률, 총 학습 시간 등을 포함합니다.
    """

    total_videos = serializers.IntegerField()
    completed_videos = serializers.IntegerField()
    overall_progress_percent = serializers.FloatField()
    total_time_spent = serializers.DurationField()


# class UserProgressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProgress
#         fields = [
#             "video",
#             "progress_percent",
#             "last_accessed",
#             "time_spent",
#             "is_completed",
#         ]

from rest_framework import serializers

from videos.models import Video
from .models import MajorCategory, MinorCategory, Enrollment
from videos.serializers import VideoSerializer


class MajorCategorySerializer(serializers.ModelSerializer):
    """
    MajorCategory(대분류) 모델을 위한 시리얼라이저.
    
    대분류 강의의 모든 필드를 직렬화/역직렬화합니다.
    """

    class Meta:
        model = MajorCategory
        fields = "__all__"


class MinorCategorySerializer(serializers.ModelSerializer):
    """
    MinorCategory(소분류) 모델을 위한 시리얼라이저.
    
    소분류의 id, 이름, 관련 대분류, 내용, 순서, 그리고 해당 소분류에 포함된 비디오 정보를 직렬화합니다.
    """

    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = MinorCategory
        fields = (
            "id",
            "name",
            "content",
            "order",
            "videos",
            "major_category",
        )

    def get_videos(self, obj):
        """
        해당 소분류에 속한 비디오들을 필터링하여 직렬화된 데이터를 반환합니다.
        
        Args:
            obj (MinorCategory): 현재 직렬화하는 MinorCategory 객체.

        Returns:
            list: 직렬화된 비디오 데이터.
        """
        videos = Video.objects.filter(minor_category=obj)
        return VideoSerializer(videos, many=True).data


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Enrollment(수강 신청) 모델을 위한 시리얼라이저.
    
    수강 신청의 id, 사용자, 대분류, 등록일, 만료일, 상태 정보를 직렬화/역직렬화하며,
    대분류 정보는 MajorCategorySerializer를 통해 중첩하여 제공합니다.
    """

    major_category = serializers.PrimaryKeyRelatedField(
        queryset=MajorCategory.objects.all()
    )

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "user",
            "major_category",
            "enrollment_date",
            "expiry_date",
            "status",
        ]
        read_only_fields = ["user", "enrollment_date", "expiry_date", "status"]

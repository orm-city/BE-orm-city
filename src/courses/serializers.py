from rest_framework import serializers

from videos.models import Video
from .models import MajorCategory, MinorCategory, Enrollment
from videos.serializers import VideoSerializer


class MajorCategorySerializer(serializers.ModelSerializer):
    """
    대분류 강의 목록 가져오기
    """

    class Meta:
        model = MajorCategory
        fields = "__all__"


class MinorCategorySerializer(serializers.ModelSerializer):
    """
    소분류(MinorCategory) 모델을 위한 시리얼라이저
    이 시리얼라이저는 소분류의 id, 이름, 관련 대분류, 내용, 순서 정보를 직렬화/역직렬화합니다.
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
        )

    def get_videos(self, obj):
        # 마이너 카테고리에 포함된 비디오만 필터링
        videos = Video.objects.filter(minor_category=obj)
        return VideoSerializer(videos, many=True).data


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    수강신청(Enrollment) 모델을 위한 시리얼라이저

    이 시리얼라이저는 수강신청의 id, 사용자, 대분류(과목), 등록일, 만료일, 상태 정보를 직렬화/역직렬화합니다.
    대분류 정보는 MajorCategorySerializer를 통해 중첩되어 제공됩니다.
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

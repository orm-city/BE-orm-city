from rest_framework import serializers
from .models import MajorCategory, MinorCategory, Enrollment

"""
    대분류 강의 목록 가져오기
"""


class MajorCategorySerializer(serializers.ModelSerializer):
    """
    대분류(MajorCategory) 모델을 위한 시리얼라이저

    이 시리얼라이저는 대분류의 id, 이름, 가격 정보를 직렬화/역직렬화합니다.
    """

    class Meta:
        model = MajorCategory
        fields = ["id", "name", "price"]


class MinorCategorySerializer(serializers.ModelSerializer):
    """
    소분류(MinorCategory) 모델을 위한 시리얼라이저

    이 시리얼라이저는 소분류의 id, 이름, 관련 대분류, 내용, 순서 정보를 직렬화/역직렬화합니다.
    """

    class Meta:
        model = MinorCategory
        fields = ["id", "name", "major_category", "content", "order"]


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    수강신청(Enrollment) 모델을 위한 시리얼라이저

    이 시리얼라이저는 수강신청의 id, 사용자, 소분류(과목), 등록일, 만료일, 상태 정보를 직렬화/역직렬화합니다.
    소분류 정보는 MinorCategorySerializer를 통해 중첩되어 제공됩니다.
    """

    minor_category = MinorCategorySerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "user",
            "minor_category",
            "enrollment_date",
            "expiry_date",
            "status",
        ]

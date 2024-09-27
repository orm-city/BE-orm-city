from rest_framework import serializers
from .models import MajorCategory

"""
    대분류 강의 목록 가져오기
"""


class MajorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MajorCategory
        fields = ["id", "name", "price"]


"""
    소분류 강의
"""


class MinorCategorySerializer(serializers.ModelSerializer):
    pass

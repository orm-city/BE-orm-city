from rest_framework import generics
from .models import MajorCategory, MinorCategory, Enrollment
from .serializers import (
    MajorCategorySerializer,
    MinorCategorySerializer,
    EnrollmentSerializer,
)


class MajorCategoryListView(generics.ListAPIView):
    """
    모든 대분류(MajorCategory) 목록을 제공하는 뷰

    이 뷰는 GET 요청에 대해 모든 대분류의 목록을 반환합니다.
    """

    queryset = MajorCategory.objects.all()
    serializer_class = MajorCategorySerializer


class MinorCategoryListView(generics.ListAPIView):
    """
    특정 대분류에 속한 소분류(MinorCategory) 목록을 제공하는 뷰

    이 뷰는 GET 요청에 대해 URL에 지정된 대분류 ID에 해당하는 소분류 목록을 반환합니다.
    소분류는 'order' 필드를 기준으로 정렬됩니다.
    """

    serializer_class = MinorCategorySerializer

    def get_queryset(self):
        major_category_id = self.kwargs.get("major_category_id")
        return MinorCategory.objects.filter(
            major_category_id=major_category_id
        ).order_by("order")


class UserEnrollmentListView(generics.ListAPIView):
    """
    현재 로그인한 사용자의 수강신청(Enrollment) 목록을 제공하는 뷰

    이 뷰는 GET 요청에 대해 현재 인증된 사용자의 모든 수강신청 정보를 반환합니다.
    """

    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

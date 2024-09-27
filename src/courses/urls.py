from django.urls import path
from .views import MajorCategoryListView, MinorCategoryListView, UserEnrollmentListView

urlpatterns = [
    path(
        "major-categories/", MajorCategoryListView.as_view(), name="major-category-list"
    ),
    # 모든 대분류 목록을 반환하는 엔드포인트
    path(
        "major-categories/<int:major_category_id>/minor-categories/",
        MinorCategoryListView.as_view(),
        name="minor-category-list",
    ),
    # 특정 대분류에 속한 소분류 목록을 반환하는 엔드포인트
    path(
        "user-enrollments/",
        UserEnrollmentListView.as_view(),
        name="user-enrollment-list",
    ),
    # 현재 로그인한 사용자의 수강신청 목록을 반환하는 엔드포인트
]

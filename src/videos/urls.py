from django.urls import path
from .views import (
    VideoCreateAPIView,
    VideoDeleteAPIView,
    VideoUpdateAPIView,
    VideoRetrieveAPIView,
    UserProgressUpdateAPIView,
    UserProgressDetailAPIView,
)

app_name = "videos"

urlpatterns = [
    # Video 관련 엔드포인트
    path("create/", VideoCreateAPIView.as_view(), name="video-create"),
    path("<int:pk>/delete/", VideoDeleteAPIView.as_view(), name="video-delete"),
    path("<int:pk>/update/", VideoUpdateAPIView.as_view(), name="video-update"),
    path(
        "<int:pk>/", VideoRetrieveAPIView.as_view(), name="video-retrieve"
    ),  # Video URL 반환
    # User Progress 관련 엔드포인트
    path(
        "progress/update/",
        UserProgressUpdateAPIView.as_view(),
        name="user-progress-update",
    ),
    path(
        "progress/<int:video_id>/",
        UserProgressDetailAPIView.as_view(),
        name="user-progress-detail",
    ),
]

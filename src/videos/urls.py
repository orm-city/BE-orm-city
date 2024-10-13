from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import VideoViewSet, UpdateUserProgressAPIView, CompleteUploadAPIView


app_name = "videos"

# DefaultRouter 설정
router = DefaultRouter()
router.register(r"", VideoViewSet, basename="video")

urlpatterns = [
    # 진행 상황 업데이트 API
    path(
        "progress/<int:video_id>",
        UpdateUserProgressAPIView.as_view(),
        name="update-progress",
    ),
    path("complete-upload/", CompleteUploadAPIView.as_view(), name="complete-upload"),
    # VideoViewSet의 라우트 포함
    path("", include(router.urls)),
]

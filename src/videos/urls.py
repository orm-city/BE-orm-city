from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, UpdateUserProgressAPIView

app_name = "videos"

# DefaultRouter 설정
router = DefaultRouter()
router.register(r"videos", VideoViewSet, basename="video")

urlpatterns = [
    # 진행 상황 업데이트 API
    path("progress/", UpdateUserProgressAPIView.as_view(), name="update-progress"),
    # VideoViewSet의 라우트 포함
    path("", include(router.urls)),
]

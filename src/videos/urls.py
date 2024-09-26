from django.urls import path
from .views import (
    VideoDeleteAPIView,
    VideoUpdateAPIView,
    VideoRetrieveAPIView,
    VideoUploadPermissionAPIView,
    UpdateUserProgressAPIView,
)

app_name = "videos"

urlpatterns = [
    path(
        "upload-permission/",
        VideoUploadPermissionAPIView.as_view(),
        name="video-upload-permission",
    ),
    path("videos/<int:pk>/update/", VideoUpdateAPIView.as_view(), name="video-update"),
    path("videos/<int:pk>/delete/", VideoDeleteAPIView.as_view(), name="video-delete"),
    path("videos/<int:pk>/", VideoRetrieveAPIView.as_view(), name="video-retrieve"),
    path(
        "user-progress/update/",
        UpdateUserProgressAPIView.as_view(),
        name="update-user-progress",
    ),
]

from django.urls import path
from .views import (
    UserProgressListView,
    UserProgressUpdateView,
    UserOverallProgressView,
    UserProgressDetailView,
)

urlpatterns = [
    path("", UserProgressListView.as_view(), name="user-progress-list"),
    path(
        "update/<int:pk>/",
        UserProgressUpdateView.as_view(),
        name="user-progress-update",
    ),
    path("overall/", UserOverallProgressView.as_view(), name="user-overall-progress"),
    path(
        "video/<int:video_id>/",
        UserProgressDetailView.as_view(),
        name="user-progress-detail",
    ),
]

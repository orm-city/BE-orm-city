from django.urls import path
from . import views

urlpatterns = [
    path(
        "overall/",
        views.UserOverallProgressView.as_view(),
        name="user-overall-progress",
    ),
    path(
        "video/<int:video_id>/",
        views.UserProgressDetailView.as_view(),
        name="user-progress-detail",
    ),
    path(
        "update/<int:video_id>/",
        views.UpdateUserProgressView.as_view(),
        name="update-user-progress",
    ),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardSummaryView,
    DailyVisitViewSet,
    DailyPaymentViewSet,
    UserLearningRecordViewSet,
    UserVideoProgressViewSet,
    ExpirationNotificationViewSet,
    StudentDashboardView,
    dashboard_view,
)

router = DefaultRouter()
router.register(r"daily-visits", DailyVisitViewSet)
router.register(r"daily-payments", DailyPaymentViewSet)
router.register(
    r"learning-records", UserLearningRecordViewSet, basename="userlearningrecord"
)
router.register(
    r"video-progress", UserVideoProgressViewSet, basename="uservideoprogress"
)
router.register(
    r"expiration-notifications",
    ExpirationNotificationViewSet,
    basename="expirationnotification",
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("", include(router.urls)),
    path("summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path(
        "student-dashboard/", StudentDashboardView.as_view(), name="student-dashboard"
    ),
]

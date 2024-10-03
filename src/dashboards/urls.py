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
)

router = DefaultRouter()
router.register(r"daily-visits", DailyVisitViewSet)
router.register(r"daily-payments", DailyPaymentViewSet)
router.register(r"learning-records", UserLearningRecordViewSet)
router.register(r"video-progress", UserVideoProgressViewSet)
router.register(r"expiration-notifications", ExpirationNotificationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path(
        "student-dashboard/", StudentDashboardView.as_view(), name="student-dashboard"
    ),
]

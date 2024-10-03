from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminUser
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .models import (
    DailyVisit,
    DailyPayment,
    UserLearningRecord,
    UserVideoProgress,
    ExpirationNotification,
)
from .serializers import (
    DashboardSummarySerializer,
    DailyVisitSerializer,
    DailyPaymentSerializer,
    UserLearningRecordSerializer,
    UserVideoProgressSerializer,
    ExpirationNotificationSerializer,
)
from missions.serializers import (
    MissionSerializer,
)  # MissionSerializer를 missions 앱에서 import
from .services import DashboardService


class DashboardSummaryView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DashboardSummarySerializer

    def get_object(self):
        return DashboardService.get_dashboard_summary()


class DailyVisitViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = DailyVisit.objects.all().order_by("-date")
    serializer_class = DailyVisitSerializer


class DailyPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = DailyPayment.objects.all().order_by("-date")
    serializer_class = DailyPaymentSerializer


class UserLearningRecordViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = UserLearningRecordSerializer

    def get_queryset(self):
        return UserLearningRecord.objects.filter(user=self.request.user).order_by(
            "-date"
        )


class UserVideoProgressViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = UserVideoProgressSerializer

    def get_queryset(self):
        return UserVideoProgress.objects.filter(
            user_progress__user=self.request.user
        ).order_by("-date")


class ExpirationNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = ExpirationNotification.objects.filter(is_sent=False).order_by(
        "notification_date"
    )
    serializer_class = ExpirationNotificationSerializer


class StudentDashboardView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLearningRecordSerializer

    def retrieve(self, request, *args, **kwargs):
        dashboard_data = DashboardService.get_student_dashboard(request.user)

        data = {
            "learning_record": UserLearningRecordSerializer(
                dashboard_data["learning_record"]
            ).data,
            "video_progress": UserVideoProgressSerializer(
                dashboard_data["video_progress"]
            ).data,
            "active_courses": dashboard_data["active_courses"],
            "completed_courses": dashboard_data["completed_courses"],
            "total_study_time": dashboard_data["total_study_time"],
            "average_daily_study_time": dashboard_data["average_daily_study_time"],
            "next_expiration": (
                ExpirationNotificationSerializer(dashboard_data["next_expiration"]).data
                if dashboard_data["next_expiration"]
                else None
            ),
            "recent_missions": MissionSerializer(
                dashboard_data["recent_missions"], many=True
            ).data,
        }

        return Response(data)

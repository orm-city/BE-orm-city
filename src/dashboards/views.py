from django.shortcuts import render

from rest_framework import generics, viewsets
from rest_framework.response import Response

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
from .services import DashboardService
from missions.serializers import MissionSerializer  

from rest_framework.permissions import AllowAny  


class DashboardSummaryView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]  # 변경
    # permission_classes = [IsAdminUser]
    serializer_class = DashboardSummarySerializer

    def get_object(self):
        return DashboardService.get_dashboard_summary()


class DailyVisitViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]  # 변경
    #   permission_classes = [IsAdminOrReadOnly]
    queryset = DailyVisit.objects.all().order_by("-date")
    serializer_class = DailyVisitSerializer


class DailyPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]  # 변경
    # permission_classes = [IsAdminOrReadOnly]
    queryset = DailyPayment.objects.all().order_by("-date")
    serializer_class = DailyPaymentSerializer


class UserLearningRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserLearningRecord.objects.all()
    serializer_class = UserLearningRecordSerializer
    # permission_classes = [IsOwnerOrAdmin]
    permission_classes = [AllowAny]  # 변경

    def get_queryset(self):
        return UserLearningRecord.objects.all().order_by("-date")  # 모든 레코드 반환


class UserVideoProgressViewSet(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [IsOwnerOrAdmin]
    permission_classes = [AllowAny]  # 변경

    serializer_class = UserVideoProgressSerializer
    queryset = UserVideoProgress.objects.all()

    def get_queryset(self):
        return UserVideoProgress.objects.all().order_by("-date")  # 모든 레코드 반환


class ExpirationNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]  # 변경
    # permission_classes = [IsAdminUser]
    queryset = ExpirationNotification.objects.filter(is_sent=False).order_by(
        "notification_date"
    )
    serializer_class = ExpirationNotificationSerializer


class StudentDashboardView(generics.RetrieveAPIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # 변경

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


def dashboard_view(request):
    return render(request, "dashboards/index.html")

from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

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


class DashboardSummaryView(generics.RetrieveAPIView):
    """
    대시보드 요약 정보를 제공하는 APIView 클래스.
    대시보드의 총 학생 수, 코스 수, 총 수익 및 평균 완료율을 반환합니다.

    Args:
        None
    
    Returns:
        Response: 대시보드 요약 정보
    """
    permission_classes = [AllowAny]  # 변경
    serializer_class = DashboardSummarySerializer

    def get_object(self):
        """
        대시보드 요약 데이터를 반환합니다.
        """
        return DashboardService.get_dashboard_summary()


class DailyVisitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    일일 방문 기록을 제공하는 ViewSet 클래스.
    각 날짜별로 학생의 고유 방문자 수 및 총 조회수를 반환합니다.
    
    Args:
        None
    
    Returns:
        Response: 일일 방문 기록 데이터
    """
    permission_classes = [AllowAny]  # 변경
    queryset = DailyVisit.objects.all().order_by("-date")
    serializer_class = DailyVisitSerializer


class DailyPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    일일 결제 기록을 제공하는 ViewSet 클래스.
    각 날짜별로 결제 정보 및 관련 데이터를 반환합니다.
    
    Args:
        None
    
    Returns:
        Response: 일일 결제 기록 데이터
    """
    permission_classes = [AllowAny]  # 변경
    queryset = DailyPayment.objects.all().order_by("-date")
    serializer_class = DailyPaymentSerializer


class UserLearningRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    사용자 학습 기록을 제공하는 ViewSet 클래스.
    사용자가 특정 날짜에 학습한 기록을 반환합니다.
    
    Args:
        None
    
    Returns:
        Response: 사용자 학습 기록 데이터
    """
    permission_classes = [AllowAny]  # 변경
    queryset = UserLearningRecord.objects.all().order_by("-date")
    serializer_class = UserLearningRecordSerializer


class UserVideoProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    사용자의 비디오 학습 진행 기록을 제공하는 ViewSet 클래스.
    사용자별로 비디오 시청 시간과 진행률을 반환합니다.
    
    Args:
        None
    
    Returns:
        Response: 사용자 비디오 학습 진행 데이터
    """
    permission_classes = [AllowAny]  # 변경
    queryset = UserVideoProgress.objects.all().order_by("-date")
    serializer_class = UserVideoProgressSerializer


class ExpirationNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    수강 만료 알림 정보를 제공하는 ViewSet 클래스.
    아직 발송되지 않은 만료 알림 목록을 반환합니다.
    
    Args:
        None
    
    Returns:
        Response: 수강 만료 알림 데이터
    """
    permission_classes = [AllowAny]  # 변경
    queryset = ExpirationNotification.objects.filter(is_sent=False).order_by(
        "notification_date"
    )
    serializer_class = ExpirationNotificationSerializer


class StudentDashboardView(generics.RetrieveAPIView):
    """
    학생의 대시보드를 제공하는 APIView 클래스.
    학생의 학습 기록, 비디오 진행률, 등록된 코스 정보를 반환합니다.
    
    Args:
        None
    
    Returns:
        Response: 학생 대시보드 데이터
    """
    permission_classes = [AllowAny]  # 변경
    serializer_class = UserLearningRecordSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        학생의 대시보드 데이터를 가져옵니다.
        """
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
    """
    대시보드 HTML 페이지를 렌더링합니다.

    Args:
        request (HttpRequest): HTTP 요청 객체.

    Returns:
        HttpResponse: 렌더링된 대시보드 HTML 페이지.
    """
    return render(request, "dashboards/index.html")

from drf_spectacular.utils import extend_schema
from .serializers import (
    DashboardSummarySerializer,
    DailyVisitSerializer,
    DailyPaymentSerializer,
    UserLearningRecordSerializer,
    UserVideoProgressSerializer,
    ExpirationNotificationSerializer,
)

# DashboardSummaryView 스키마 정의
dashboard_summary_schema = extend_schema(
    summary="대시보드 요약 정보 조회",
    description="대시보드의 총 학생 수, 코스 수, 총 수익 및 평균 완료율 등의 요약 정보를 제공합니다.",
    responses={200: DashboardSummarySerializer}
)

# DailyVisitViewSet 스키마 정의
daily_visit_schemas = {
    'list': extend_schema(
        summary="일일 방문 기록 조회",
        description="날짜별로 고유 방문자 수와 총 조회수를 반환합니다.",
        responses={200: DailyVisitSerializer(many=True)}
    )
}

# DailyPaymentViewSet 스키마 정의
daily_payment_schemas = {
    'list': extend_schema(
        summary="일일 결제 기록 조회",
        description="날짜별로 결제 정보 및 관련 데이터를 반환합니다.",
        responses={200: DailyPaymentSerializer(many=True)}
    )
}

# UserLearningRecordViewSet 스키마 정의
user_learning_record_schemas = {
    'list': extend_schema(
        summary="사용자 학습 기록 조회",
        description="사용자가 특정 날짜에 학습한 기록을 반환합니다.",
        responses={200: UserLearningRecordSerializer(many=True)}
    )
}

# UserVideoProgressViewSet 스키마 정의
user_video_progress_schemas = {
    'list': extend_schema(
        summary="사용자 비디오 학습 진행 조회",
        description="사용자의 비디오 시청 시간과 진행률을 반환합니다.",
        responses={200: UserVideoProgressSerializer(many=True)}
    )
}

# ExpirationNotificationViewSet 스키마 정의
expiration_notification_schemas = {
    'list': extend_schema(
        summary="수강 만료 알림 조회",
        description="아직 발송되지 않은 수강 만료 알림 목록을 반환합니다.",
        responses={200: ExpirationNotificationSerializer(many=True)}
    )
}

# StudentDashboardView 스키마 정의
student_dashboard_schema = extend_schema(
    summary="학생 대시보드 조회",
    description="학생의 학습 기록, 비디오 진행률, 등록된 코스 정보를 반환합니다.",
    responses={200: UserLearningRecordSerializer}
)

from rest_framework import serializers

from accounts.models import CustomUser
from courses.models import MajorCategory, MinorCategory
from payment.models import Payment
from .models import (
    DailyVisit,
    DailyPayment,
    UserLearningRecord,
    UserVideoProgress,
    ExpirationNotification,
)


class CustomUserSerializer(serializers.ModelSerializer):
    """
    사용자(CustomUser) 모델의 데이터를 직렬화하는 클래스.

    Fields:
        id (int): 사용자 ID.
        username (str): 사용자 이름.
        email (str): 사용자 이메일.
        role (str): 사용자 역할.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role"]


class MajorCategorySerializer(serializers.ModelSerializer):
    """
    대분류(MajorCategory) 모델의 데이터를 직렬화하는 클래스.

    Fields:
        id (int): 대분류 ID.
        name (str): 대분류 이름.
    """

    class Meta:
        model = MajorCategory
        fields = ["id", "name"]


class MinorCategorySerializer(serializers.ModelSerializer):
    """
    소분류(MinorCategory) 모델의 데이터를 직렬화하는 클래스.

    Fields:
        id (int): 소분류 ID.
        name (str): 소분류 이름.
        major_category (MajorCategory): 관련 대분류.
    """

    class Meta:
        model = MinorCategory
        fields = ["id", "name", "major_category"]


class PaymentSerializer(serializers.ModelSerializer):
    """
    결제(Payment) 모델의 데이터를 직렬화하는 클래스.

    Fields:
        id (int): 결제 ID.
        total_amount (Decimal): 결제 총액.
        payment_date (datetime): 결제일 (형식: 'YYYY-MM-DD HH:MM:SS').
        payment_status (str): 결제 상태.
    """

    payment_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Payment
        fields = ["id", "total_amount", "payment_date", "payment_status"]


class DailyVisitSerializer(serializers.ModelSerializer):
    """
    일일 방문 기록(DailyVisit) 모델의 데이터를 직렬화하는 클래스.

    Fields:
        date (date): 방문 날짜.
        student_unique_visitors (int): 학생 고유 방문자 수.
        student_total_views (int): 학생 총 조회 수.
    """

    date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = DailyVisit
        fields = ["date", "student_unique_visitors", "student_total_views"]


class DailyPaymentSerializer(serializers.ModelSerializer):
    """
    일별 결제 기록(DailyPayment) 모델의 데이터를 직렬화하는 클래스.

    Fields:
        id (int): 결제 기록 ID.
        date (date): 결제일.
        payment (Payment): 결제 정보.
        user (CustomUser): 결제한 사용자 정보.
        major_category (MajorCategory): 결제가 이루어진 대분류 정보.
    """

    payment = PaymentSerializer()
    user = CustomUserSerializer(source="payment.user")
    major_category = MajorCategorySerializer(source="payment.major_category")
    date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = DailyPayment
        fields = ["id", "date", "payment", "user", "major_category"]


class UserLearningRecordSerializer(serializers.ModelSerializer):
    """
    사용자 학습 기록(UserLearningRecord) 모델의 데이터를 직렬화하는 클래스.

    Fields:
        id (int): 학습 기록 ID.
        user (CustomUser): 사용자 정보.
        date (date): 학습 날짜.
        major_category (MajorCategory): 학습한 대분류.
        progress_percent (float): 학습 진행률.
    """

    user = CustomUserSerializer()
    major_category = MajorCategorySerializer()
    date = serializers.DateField(format="%Y-%m-%d")
    progress_percent = serializers.FloatField(read_only=True)

    class Meta:
        model = UserLearningRecord
        fields = ["id", "user", "date", "major_category", "progress_percent"]


class UserVideoProgressSerializer(serializers.ModelSerializer):
    """
    사용자 비디오 학습 진행(UserVideoProgress) 모델의 데이터를 직렬화하는 클래스.

    Fields:
        id (int): 진행 기록 ID.
        user (CustomUser): 사용자 정보.
        video (str): 학습한 비디오 제목.
        date (date): 학습 날짜.
        daily_watch_duration (int): 일일 시청 시간(초 단위).
        total_watch_duration (duration): 총 시청 시간.
        progress_percent (float): 학습 진행률.
    """

    user = CustomUserSerializer(source="user_progress.user")
    video = serializers.StringRelatedField(source="user_progress.video")
    date = serializers.DateField(format="%Y-%m-%d")
    total_watch_duration = serializers.DurationField(read_only=True)
    progress_percent = serializers.FloatField(read_only=True)

    class Meta:
        model = UserVideoProgress
        fields = [
            "id",
            "user",
            "video",
            "date",
            "daily_watch_duration",
            "total_watch_duration",
            "progress_percent",
        ]


class ExpirationNotificationSerializer(serializers.ModelSerializer):
    """
    수강 만료 알림(ExpirationNotification) 모델의 데이터를 직렬화하는 클래스.

    Fields:
        id (int): 알림 ID.
        user (CustomUser): 사용자 정보.
        major_category (MajorCategory): 만료된 대분류 정보.
        notification_date (date): 알림 날짜.
        is_sent (bool): 알림 발송 여부.
        days_until_expiry (int): 만료일까지 남은 일수.
    """

    user = CustomUserSerializer()
    major_category = MajorCategorySerializer(source="enrollment.major_category")
    notification_date = serializers.DateField(format="%Y-%m-%d")
    days_until_expiry = serializers.IntegerField(read_only=True)

    class Meta:
        model = ExpirationNotification
        fields = [
            "id",
            "user",
            "major_category",
            "notification_date",
            "is_sent",
            "days_until_expiry",
        ]


# 대시보드 요약 데이터를 위한 시리얼라이저
class DashboardSummarySerializer(serializers.Serializer):
    """
    대시보드 요약 데이터를 직렬화하는 클래스.

    Fields:
        total_students (int): 총 학생 수.
        total_courses (int): 총 강의 수.
        total_revenue (Decimal): 총 수익.
        avg_completion_rate (float): 평균 학습 완료율.
    """

    total_students = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_completion_rate = serializers.FloatField()


# 대시보드 상세 데이터를 위한 시리얼라이저
class DashboardDetailSerializer(serializers.Serializer):
    """
    대시보드 상세 데이터를 직렬화하는 클래스.

    Fields:
        daily_visits (DailyVisitSerializer): 일일 방문 기록.
        daily_payments (DailyPaymentSerializer): 일일 결제 기록.
        user_learning_records (UserLearningRecordSerializer): 사용자 학습 기록.
        user_video_progress (UserVideoProgressSerializer): 사용자 비디오 학습 진행 기록.
        expiration_notifications (ExpirationNotificationSerializer): 수강 만료 알림.
    """

    daily_visits = DailyVisitSerializer(many=True)
    daily_payments = DailyPaymentSerializer(many=True)
    user_learning_records = UserLearningRecordSerializer(many=True)
    user_video_progress = UserVideoProgressSerializer(many=True)
    expiration_notifications = ExpirationNotificationSerializer(many=True)

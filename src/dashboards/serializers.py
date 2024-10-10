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
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role"]


class MajorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MajorCategory
        fields = ["id", "name"]


class MinorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MinorCategory
        fields = ["id", "name", "major_category"]


class PaymentSerializer(serializers.ModelSerializer):
    payment_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Payment
        fields = ["id", "total_amount", "payment_date", "payment_status"]


class DailyVisitSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = DailyVisit
        fields = ["date", "student_unique_visitors", "student_total_views"]


class DailyPaymentSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()
    user = CustomUserSerializer(source="payment.user")
    major_category = MajorCategorySerializer(source="payment.major_category")
    date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = DailyPayment
        fields = ["id", "date", "payment", "user", "major_category"]


class UserLearningRecordSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    major_category = MajorCategorySerializer()
    date = serializers.DateField(format="%Y-%m-%d")
    progress_percent = serializers.FloatField(read_only=True)

    class Meta:
        model = UserLearningRecord  # DailyVisit에서 UserLearningRecord로 변경
        fields = [
            "id",  # id 필드 추가
            "user",
            "date",
            "major_category",
            "progress_percent",
            # 필요한 경우 다른 필드들도 추가
        ]


class UserVideoProgressSerializer(serializers.ModelSerializer):
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
    total_students = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_completion_rate = serializers.FloatField()


# 대시보드 상세 데이터를 위한 시리얼라이저
class DashboardDetailSerializer(serializers.Serializer):
    daily_visits = DailyVisitSerializer(many=True)
    daily_payments = DailyPaymentSerializer(many=True)
    user_learning_records = UserLearningRecordSerializer(many=True)
    user_video_progress = UserVideoProgressSerializer(many=True)
    expiration_notifications = ExpirationNotificationSerializer(many=True)

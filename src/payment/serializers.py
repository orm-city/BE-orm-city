from rest_framework import serializers
from django.utils import timezone
from .models import Payment
from courses.models import MajorCategory


class PaymentCreateSerializer(serializers.Serializer):
    major_category_id = serializers.PrimaryKeyRelatedField(
        queryset=MajorCategory.objects.all(), write_only=True
    )

    def create(self, validated_data):
        user = self.context["request"].user
        major_category = validated_data["major_category_id"]
        return Payment.objects.create(
            user=user,
            major_category=major_category,
            total_amount=major_category.price,
            payment_status="PENDING",
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class PaymentDetailSerializer(serializers.ModelSerializer):
    is_refundable = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "merchant_uid",
            "imp_uid",
            "total_amount",
            "payment_status",
            "payment_date",
            "is_refundable",
        ]

    def get_is_refundable(self, obj):
        # 환불 가능 여부를 결정하는 로직
        # 예: 결제 후 7일 이내이고, 결제 상태가 'paid'인 경우
        return (
            timezone.now() - obj.payment_date
        ).days <= 7 and obj.payment_status == "paid"

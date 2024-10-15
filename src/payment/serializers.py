from django.utils import timezone

from rest_framework import serializers

from courses.models import MajorCategory

from .models import Payment


class PaymentCreateSerializer(serializers.Serializer):
    """
    결제 생성 시리얼라이저.

    사용자가 선택한 major_category_id를 받아 결제 내역을 생성합니다.

    속성:
        major_category_id (PrimaryKeyRelatedField): 사용자가 선택한 수강 카테고리 ID.
    """

    major_category_id = serializers.PrimaryKeyRelatedField(
        queryset=MajorCategory.objects.all(), write_only=True
    )

    def create(self, validated_data):
        """
        유효성 검사를 통과한 데이터를 기반으로 Payment 객체를 생성합니다.

        Args:
            validated_data (dict): 유효성 검사를 통과한 데이터.

        Returns:
            Payment: 생성된 Payment 객체.
        """
        user = self.context["request"].user
        major_category = validated_data["major_category_id"]
        return Payment.objects.create(
            user=user,
            major_category=major_category,
            total_amount=major_category.price,
            payment_status="PENDING",
        )


class PaymentSerializer(serializers.ModelSerializer):
    """
    Payment 모델에 대한 모든 필드를 포함하는 시리얼라이저.

    Payment 모델의 모든 필드를 직렬화합니다.
    """

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentDetailSerializer(serializers.ModelSerializer):
    """
    결제 상세 정보를 제공하는 시리얼라이저.

    결제 정보와 환불 가능 여부 등을 직렬화합니다.

    속성:
        is_refundable (SerializerMethodField): 환불 가능 여부를 반환하는 필드.
    """
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
            "refund_deadline",
        ]

    def get_is_refundable(self, obj):
        """
        결제의 환불 가능 여부를 결정합니다.

        환불 가능 기간(결제 후 7일 이내)이 경과하지 않고 결제 상태가 'paid'일 경우 환불이 가능합니다.

        Args:
            obj (Payment): 현재 Payment 객체.

        Returns:
            bool: 환불 가능 여부.
        """
        return (
            (timezone.now() - obj.payment_date).days <= 7 and obj.payment_status == "paid"
        )

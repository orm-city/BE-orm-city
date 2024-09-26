from rest_framework import serializers
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

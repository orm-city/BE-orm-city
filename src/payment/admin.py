from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "major_category",
        "total_amount",
        "payment_status",
        "payment_status",
    )  # Admin에서 표시할 필드
    list_filter = ("payment_status", "payment_status")  # 필터 가능한 필드
    search_fields = (
        "user__username",
        "major_category__name",
    )  # 검색 가능한 필드 (유저와 카테고리)

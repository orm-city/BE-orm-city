from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    결제 정보(Payment) 관리를 위한 Admin 클래스.

    Admin 페이지에서 결제 정보에 대한 목록을 표시하고, 필터 및 검색 기능을 제공합니다.
    """

    list_display = (
        "user",
        "major_category",
        "total_amount",
        "payment_status",
        "refund_amount",
        "refund_status",
    )  # Admin에서 표시할 필드
    list_filter = ("payment_status", "refund_status")  # 필터 가능한 필드
    search_fields = (
        "user__username",
        "major_category__name",
    )  # 검색 가능한 필드 (유저와 카테고리)

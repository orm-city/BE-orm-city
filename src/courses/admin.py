from django.contrib import admin

from .models import Enrollment, MajorCategory, MinorCategory


@admin.register(MajorCategory)
class MajorCategoryAdmin(admin.ModelAdmin):
    """
    MajorCategory 모델의 관리 인터페이스 정의.

    Admin 화면에서 MajorCategory 객체의 이름과 가격을 표시하고,
    이름으로 검색할 수 있습니다.
    """
    list_display = ("name", "price")  # Admin 리스트에서 보여줄 필드
    search_fields = ("name",)  # 검색할 필드


@admin.register(MinorCategory)
class MinorCategoryAdmin(admin.ModelAdmin):
    """
    MinorCategory 모델의 관리 인터페이스 정의.

    Admin 화면에서 MinorCategory 객체의 이름, 관련 MajorCategory, 순서, 진행률을 표시하고,
    이름과 MajorCategory로 검색할 수 있으며, MajorCategory로 필터링할 수 있습니다.
    """
    list_display = ("name", "major_category", "order", "progress_percent")
    search_fields = ("name", "major_category__name")
    list_filter = ("major_category",)
    ordering = ("order",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """
    Enrollment 모델의 관리 인터페이스 정의.

    Admin 화면에서 Enrollment 객체의 사용자, MajorCategory, 수강 신청 날짜, 만료 날짜, 상태를 표시하고,
    사용자 이름과 MajorCategory 이름으로 검색할 수 있으며, 상태와 날짜로 필터링할 수 있습니다.
    수강 신청 날짜 기준으로 계층적 날짜 탐색을 할 수 있습니다.
    """
    list_display = (
        "user",
        "major_category",
        "enrollment_date",
        "expiry_date",
        "status",
    )
    search_fields = ("user__username", "major_category__name")
    list_filter = ("status", "major_category", "enrollment_date", "expiry_date")
    date_hierarchy = "enrollment_date"
    raw_id_fields = ("user", "major_category")  # 외래 키 필드를 ID로 표시

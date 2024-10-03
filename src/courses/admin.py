from django.contrib import admin
from .models import Enrollment, MajorCategory, MinorCategory


@admin.register(MajorCategory)
class MajorCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "price")  # Admin 리스트에서 보여줄 필드
    search_fields = ("name",)  # 검색할 필드


@admin.register(MinorCategory)
class MinorCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "major_category", "order", "progress_percent")
    search_fields = ("name", "major_category__name")
    list_filter = ("major_category",)
    ordering = ("order",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
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
    raw_id_fields = ("user", "major_category")

from django.contrib import admin
from .models import MajorCategory


@admin.register(MajorCategory)
class MajorCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "price")  # Admin 리스트에서 보여줄 필드
    search_fields = ("name",)  # 검색할 필드

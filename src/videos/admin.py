from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("name", "minor_category", "duration", "order", "created_at")
    list_filter = ("minor_category", "created_at")
    search_fields = ("name", "description")
    ordering = ("order", "created_at")
    # 영상의 순서를 관리하기 위해 ordering 추가

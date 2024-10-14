from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Video 모델에 대한 관리자 인터페이스를 정의합니다.

    Attributes:
        list_display (tuple): 관리자가 비디오 목록에서 볼 수 있는 필드들입니다. 
            비디오의 이름, 소분류 카테고리, 길이, 순서, 생성일자를 표시합니다.
        list_filter (tuple): 관리자가 필터링할 수 있는 필드입니다. 
            소분류 카테고리 및 생성일자 기준으로 필터링이 가능합니다.
        search_fields (tuple): 관리자가 비디오 목록에서 검색할 수 있는 필드입니다. 
            비디오의 이름과 설명을 기준으로 검색할 수 있습니다.
        ordering (tuple): 비디오 목록을 정렬하는 기준입니다. 
            비디오의 순서(order) 및 생성일(created_at) 순으로 정렬됩니다.
    """

    list_display = ("name", "minor_category", "duration", "order", "created_at")
    list_filter = ("minor_category", "created_at")
    search_fields = ("name", "description")
    ordering = ("order", "created_at")
    # 영상의 순서를 관리하기 위해 ordering 추가

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    CustomUser 모델을 위한 관리자 인터페이스

    이 클래스는 Django의 기본 UserAdmin을 확장하여 CustomUser 모델의
    추가 필드들을 관리자 페이지에서 효과적으로 다룰 수 있도록 합니다.

    주요 기능:
    - 사용자 정보 표시 및 편집
    - 권한 관리
    - 구독 상태 확인
    - 사용자 검색 및 필터링
    """

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "nickname",
                    "gender",
                    "contact_number",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (
            _("WinniVersity info"),
            {"fields": ("role", "total_study_time")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "role",
                    "nickname",
                ),
            },
        ),
    )
    list_display = (
        "username",
        "email",
        "get_full_name",
        "role",
        "is_staff",
        "total_study_time",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "role", "gender")
    search_fields = ("username", "first_name", "last_name", "email", "nickname")
    ordering = ("username",)

    def get_full_name(self, obj):
        """
        사용자의 전체 이름을 반환합니다.

        Args:
            obj (CustomUser): 사용자 객체

        Returns:
            str: 사용자의 전체 이름 또는 닉네임
        """
        return obj.get_full_name()

    get_full_name.short_description = "이름"


admin.site.register(CustomUser, CustomUserAdmin)

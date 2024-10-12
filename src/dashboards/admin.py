from django.contrib import admin

from .models import (
    DailyVisit,
    DailyPayment,
    UserLearningRecord,
    UserVideoProgress,
    ExpirationNotification,
)


@admin.register(DailyVisit)
class DailyVisitAdmin(admin.ModelAdmin):
    list_display = ("date", "student_unique_visitors", "student_total_views")
    list_filter = ("date",)


@admin.register(DailyPayment)
class DailyPaymentAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "major_category", "amount")
    list_filter = ("date", "payment__major_category")  # 수정된 부분

    def user(self, obj):
        return obj.payment.user

    def major_category(self, obj):
        return obj.payment.major_category


@admin.register(UserLearningRecord)
class UserLearningRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "major_category")
    list_filter = ("date", "major_category")


@admin.register(UserVideoProgress)
class UserVideoProgressAdmin(admin.ModelAdmin):
    list_display = (
        "get_user",
        "get_video",
        "date",
    )
    list_filter = (
        "date",
        "user_progress__user",
    )
    list_select_related = (
        "user_progress",
        "user_progress__user",
        "user_progress__video",
    )  # 관련 객체 미리 로드
    exclude = ("daily_watch_duration", "progress_percent")  # 이 줄을 추가합니다

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["user_progress"].required = False
        return form

    def get_user(self, obj):
        return obj.user_progress.user if obj.user_progress else None

    get_user.short_description = "User"
    get_user.admin_order_field = "user_progress__user"

    def get_video(self, obj):
        return obj.user_progress.video if obj.user_progress else None

    get_video.short_description = "Video"
    get_video.admin_order_field = "user_progress__video"


@admin.register(ExpirationNotification)
class ExpirationNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "enrollment", "notification_date", "is_sent")
    list_filter = ("notification_date", "is_sent")

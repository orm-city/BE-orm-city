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
    """
    DailyVisit 모델에 대한 Admin 설정 클래스.

    Attributes:
        list_display (tuple): Admin 리스트에서 표시할 필드.
        list_filter (tuple): 필터링할 필드.
    """

    list_display = ("date", "student_unique_visitors", "student_total_views")
    list_filter = ("date",)


@admin.register(DailyPayment)
class DailyPaymentAdmin(admin.ModelAdmin):
    """
    DailyPayment 모델에 대한 Admin 설정 클래스.

    Attributes:
        list_display (tuple): Admin 리스트에서 표시할 필드.
        list_filter (tuple): 필터링할 필드.

    Methods:
        user (obj): 결제와 관련된 사용자를 반환.
        major_category (obj): 결제와 관련된 대분류를 반환.
    """

    list_display = ("date", "user", "major_category", "amount")
    list_filter = ("date", "payment__major_category")  # 수정된 부분

    def user(self, obj):
        """
        결제와 관련된 사용자를 반환.

        Args:
            obj: DailyPayment 객체.

        Returns:
            User: 결제와 연결된 사용자.
        """
        return obj.payment.user

    def major_category(self, obj):
        """
        결제와 관련된 대분류를 반환.

        Args:
            obj: DailyPayment 객체.

        Returns:
            MajorCategory: 결제와 연결된 대분류.
        """
        return obj.payment.major_category


@admin.register(UserLearningRecord)
class UserLearningRecordAdmin(admin.ModelAdmin):
    """
    UserLearningRecord 모델에 대한 Admin 설정 클래스.

    Attributes:
        list_display (tuple): Admin 리스트에서 표시할 필드.
        list_filter (tuple): 필터링할 필드.
    """

    list_display = ("user", "date", "major_category")
    list_filter = ("date", "major_category")


@admin.register(UserVideoProgress)
class UserVideoProgressAdmin(admin.ModelAdmin):
    """
    UserVideoProgress 모델에 대한 Admin 설정 클래스.

    Attributes:
        list_display (tuple): Admin 리스트에서 표시할 필드.
        list_filter (tuple): 필터링할 필드.
        list_select_related (tuple): 미리 로드할 관련 객체 필드.
        exclude (tuple): Admin 양식에서 제외할 필드.

    Methods:
        get_form (request, obj, kwargs): Admin 양식에서 user_progress 필드의 필수 여부를 설정.
        get_user (obj): 관련된 사용자를 반환.
        get_video (obj): 관련된 비디오를 반환.
    """

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
    )
    exclude = ("daily_watch_duration", "progress_percent")

    def get_form(self, request, obj=None, **kwargs):
        """
        Admin 양식에서 user_progress 필드의 필수 여부를 설정.

        Args:
            request: 요청 객체.
            obj: 대상 객체.
            kwargs: 추가 인자.

        Returns:
            form: 수정된 Admin 양식.
        """
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["user_progress"].required = False
        return form

    def get_user(self, obj):
        """
        관련된 사용자를 반환.

        Args:
            obj: UserVideoProgress 객체.

        Returns:
            User: 관련된 사용자.
        """
        return obj.user_progress.user if obj.user_progress else None

    get_user.short_description = "User"
    get_user.admin_order_field = "user_progress__user"

    def get_video(self, obj):
        """
        관련된 비디오를 반환.

        Args:
            obj: UserVideoProgress 객체.

        Returns:
            Video: 관련된 비디오.
        """
        return obj.user_progress.video if obj.user_progress else None

    get_video.short_description = "Video"
    get_video.admin_order_field = "user_progress__video"


@admin.register(ExpirationNotification)
class ExpirationNotificationAdmin(admin.ModelAdmin):
    """
    ExpirationNotification 모델에 대한 Admin 설정 클래스.

    Attributes:
        list_display (tuple): Admin 리스트에서 표시할 필드.
        list_filter (tuple): 필터링할 필드.
    """

    list_display = ("user", "enrollment", "notification_date", "is_sent")
    list_filter = ("notification_date", "is_sent")

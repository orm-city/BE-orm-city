from rest_framework import permissions

from .models import Enrollment


class CanViewUserProgress(permissions.BasePermission):
    """
    사용자의 학습 진행률 조회 권한을 확인하는 커스텀 권한 클래스.

    권한 부여 조건:
    - 관리자와 매니저는 모든 사용자의 진행률을 볼 수 있습니다.
    - 학생은 자신이 등록한 강의(enrollment 상태가 active 또는 complete인 경우)의 진행률만 볼 수 있습니다.
    """

    def has_permission(self, request, view):
        """
        주어진 요청에 대해 권한이 있는지 확인하는 메서드.

        Args:
            request (Request): 현재 HTTP 요청 객체.
            view (View): 현재 요청된 view 객체.

        Returns:
            bool: 권한이 있으면 True, 없으면 False를 반환합니다.
        """
        # 인증되지 않은 사용자는 권한이 없음
        if not request.user.is_authenticated:
            return False

        # 관리자와 매니저는 모든 진행률을 볼 수 있음
        if request.user.role in ["admin", "manager"]:
            return True

        # 학생의 경우, 특정 조건을 만족해야 함
        if request.user.role == "student":
            # UserProgressListView나 UserOverallProgressView의 경우
            if view.__class__.__name__ in [
                "UserProgressListView",
                "UserOverallProgressView",
            ]:
                # 사용자의 모든 활성 수강 신청을 확인
                active_enrollments = Enrollment.objects.filter(
                    user=request.user, status__in=["active", "completed"]
                ).exists()
                return active_enrollments

            # UserProgressDetailView나 UserProgressUpdateView의 경우
            elif view.__class__.__name__ in [
                "UserProgressDetailView",
                "UserProgressUpdateView",
            ]:
                video_id = view.kwargs.get("pk") or view.kwargs.get("video_id")
                if not video_id:
                    return False

                # 해당 비디오의 대분류에 대한 활성 수강 신청이 있는지 확인
                active_enrollment = Enrollment.objects.filter(
                    user=request.user,
                    major_category__minor_categories__videos__id=video_id,
                    status__in=["active", "completed"],
                ).exists()
                return active_enrollment

        return False

    def has_object_permission(self, request, view, obj):
        """
        객체 수준에서의 권한을 확인하는 메서드.

        Args:
            request (Request): 현재 HTTP 요청 객체.
            view (View): 현재 요청된 view 객체.
            obj (Model): 권한을 확인할 객체.

        Returns:
            bool: 객체에 대한 권한이 있으면 True, 없으면 False를 반환합니다.
        """
        # 관리자와 매니저는 모든 객체에 대해 권한이 있음
        if request.user.role in ["admin", "manager"]:
            return True

        # 학생의 경우, 자신의 진행률 객체에 대해서만 권한이 있음
        if request.user.role == "student":
            if obj.user == request.user:
                # 해당 비디오의 대분류에 대한 활성 수강 신청이 있는지 확인
                active_enrollment = Enrollment.objects.filter(
                    user=request.user,
                    major_category=obj.video.minor_category.major_category,
                    status__in=["active", "completed"],
                ).exists()
                return active_enrollment

        return False

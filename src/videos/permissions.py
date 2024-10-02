from rest_framework import permissions

from courses.models import Enrollment
from videos.models import Video


class IsAdminUser(permissions.BasePermission):
    """
    관리자만 접근 가능하도록 하는 권한 클래스.
    """

    def has_permission(self, request, view):
        # 요청한 사용자가 로그인되어 있고, role이 admin인 경우만 허용
        return request.user.is_authenticated and request.user.role == "admin"


class IsEnrolledOrAdmin(permissions.BasePermission):
    """
    관리자이거나, 해당 비디오의 소속 강의에 등록된 사용자만 접근 가능하도록 하는 권한 클래스.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == "admin":
            return True

        # 일반 사용자의 경우, 비디오의 소속 강의에 등록되었는지 확인
        video_pk = view.kwargs.get("pk")
        try:
            video = Video.objects.get(pk=video_pk)
            minor_category = video.minor_category
            major_category = minor_category.major_category

            # 사용자가 해당 MajorCategory에 등록되었는지 확인 (status가 active 또는 completed인 경우)
            enrollment = Enrollment.objects.filter(
                user=request.user,
                major_category=major_category,
                status__in=["active", "completed"],
            ).exists()
            return enrollment
        except Video.DoesNotExist:
            return False

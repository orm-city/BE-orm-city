from rest_framework import permissions

from courses.models import Enrollment


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
        # 관리자는 항상 허용
        if request.user.is_authenticated and request.user.role == "admin":
            return True

        # 비디오 목록 조회일 경우
        if view.action == "list":
            return Enrollment.objects.filter(
                user=request.user, status__in=["active", "completed"]
            ).exists()

        # 단일 비디오 조회일 경우, 객체 수준에서 권한 체크 진행
        return True  # 임시로 True 반환

    def has_object_permission(self, request, view, obj):
        # 관리자는 항상 허용
        if request.user.is_authenticated and request.user.role == "admin":
            return True

        # 비디오가 속한 major_category와 사용자 등록 상태 확인
        major_category = obj.minor_category.major_category
        return Enrollment.objects.filter(
            user=request.user,
            major_category=major_category,
            status__in=["active", "completed"],
        ).exists()

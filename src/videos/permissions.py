from rest_framework.permissions import BasePermission


class IsManagerOrAdmin(BasePermission):
    """
    사용자가 manager 또는 admin일 경우에만 접근 허용.
    """

    def has_permission(self, request, view):
        return request.user.role in ["manager", "admin"]


class IsEnrolledOrAdminOrManager(BasePermission):
    """
    사용자가 video에 enrolled 상태이거나, manager 또는 admin일 경우에만 접근 허용.
    """

    def has_permission(self, request, view):
        enrollment = getattr(request.user, "enrollment", None)
        return (
            enrollment and enrollment.status in ["completed", "active"]
        ) or request.user.role in ["manager", "admin"]

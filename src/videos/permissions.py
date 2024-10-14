from rest_framework.permissions import BasePermission


class IsManagerOrAdmin(BasePermission):
    """
    권한 클래스: 사용자가 'manager' 또는 'admin' 역할을 가지고 있을 때만 접근을 허용.

    Returns:
        bool: 사용자가 manager 또는 admin일 경우 True, 그렇지 않으면 False.
    """

    def has_permission(self, request, view):
        """
        사용자가 'manager' 또는 'admin' 역할을 가지고 있는지 확인.

        Args:
            request (Request): HTTP 요청 객체.
            view (View): 현재 뷰 객체.

        Returns:
            bool: 사용자가 manager 또는 admin일 경우 True, 그렇지 않으면 False.
        """
        return request.user.role in ["manager", "admin"]


class IsEnrolledOrAdminOrManager(BasePermission):
    """
    권한 클래스: 사용자가 video에 'enrolled' 상태이거나, 'manager' 또는 'admin' 역할일 때만 접근을 허용.

    Returns:
        bool: 사용자가 해당 video에 대한 유효한 수강 상태이거나 관리자 역할일 경우 True, 그렇지 않으면 False.
    """

    def has_permission(self, request, view):
        """
        사용자가 video에 대한 'enrollment' 상태이거나 'manager', 'admin' 역할인지 확인.

        Args:
            request (Request): HTTP 요청 객체.
            view (View): 현재 뷰 객체.

        Returns:
            bool: 사용자가 video에 대한 유효한 수강 상태 또는 관리자 역할일 경우 True, 그렇지 않으면 False.
        """
        enrollment = getattr(request.user, "enrollments", None)
        enrollment = enrollment.get(user=request.user.id)
        return (
            enrollment and enrollment.status in ["completed", "active"]
        ) or request.user.role in ["manager", "admin"]

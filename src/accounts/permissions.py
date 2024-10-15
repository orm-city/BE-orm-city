from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    관리자 권한을 확인하는 커스텀 권한 클래스.

    메서드:
        has_permission: 요청한 사용자가 인증되었으며 'admin' 역할을 가지고 있는지 확인합니다.
    """

    def has_permission(self, request, view):
        """
        요청한 사용자가 인증된 'admin'인지 여부를 확인합니다.

        Args:
            request (HttpRequest): 현재 요청 객체.
            view (View): 현재 뷰 객체.

        Returns:
            bool: 사용자가 'admin' 역할을 가지고 있으면 True, 아니면 False.
        """
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsManagerOrAdminUser(permissions.BasePermission):
    """
    관리자 또는 관리자인지 확인하는 커스텀 권한 클래스.

    메서드:
        has_permission: 요청한 사용자가 인증되었으며 'manager' 또는 'admin' 역할을 가지고 있는지 확인합니다.
    """

    def has_permission(self, request, view):
        """
        요청한 사용자가 인증된 'manager' 또는 'admin'인지 여부를 확인합니다.

        Args:
            request (HttpRequest): 현재 요청 객체.
            view (View): 현재 뷰 객체.

        Returns:
            bool: 사용자가 'manager' 또는 'admin' 역할을 가지고 있으면 True, 아니면 False.
        """
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["manager", "admin"]
        )


class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    소유자, 관리자, 또는 관리자인지 확인하는 커스텀 권한 클래스.

    메서드:
        has_object_permission: 요청한 사용자가 객체의 소유자이거나, 'manager' 또는 'admin' 역할을 가지고 있는지 확인합니다.
    """

    def has_object_permission(self, request, view, obj):
        """
        요청한 사용자가 객체의 소유자이거나, 'manager' 또는 'admin'인지 여부를 확인합니다.

        Args:
            request (HttpRequest): 현재 요청 객체.
            view (View): 현재 뷰 객체.
            obj: 접근하려는 객체.

        Returns:
            bool: 사용자가 객체의 소유자이거나 'manager' 또는 'admin'이면 True, 아니면 False.
        """
        if request.user.role in ["manager", "admin"]:
            return True
        return obj == request.user

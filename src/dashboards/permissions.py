from rest_framework.permissions import BasePermission

from core.permissions import IsAdminUser


class IsAdminOrReadOnly(BasePermission):
    """
    관리자에게는 모든 권한을 부여하고, 그 외의 사용자는 읽기 전용 권한을 부여하는 권한 클래스입니다.

    Methods:
        has_permission(request, view): 요청이 읽기 전용(GET, HEAD, OPTIONS)인 경우에는 모든 사용자가 접근 가능하며,
                                       그렇지 않으면 관리자에게만 접근 권한을 부여합니다.
    """

    def has_permission(self, request, view):
        """
        요청된 메서드에 따라 권한을 부여합니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (APIView): 요청이 발생한 뷰.

        Returns:
            bool: 읽기 전용 메서드(GET, HEAD, OPTIONS)인 경우 True, 관리자만 접근 가능한 경우 True, 그 외는 False.
        """
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return IsAdminUser().has_permission(request, view)


class IsOwnerOrAdmin(BasePermission):
    """
    객체의 소유자이거나 관리자일 때만 접근을 허용하는 권한 클래스입니다.

    Methods:
        has_object_permission(request, view, obj): 객체의 소유자나 관리자에게만 접근 권한을 부여합니다.
    """

    def has_object_permission(self, request, view, obj):
        """
        객체의 소유자이거나 관리자일 경우에만 권한을 부여합니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (APIView): 요청이 발생한 뷰.
            obj (Model): 요청된 객체.

        Returns:
            bool: 객체의 소유자이거나 관리자일 경우 True, 그 외는 False.
        """
        return obj.user == request.user or IsAdminUser().has_permission(request, view)

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    관리자 사용자에게는 모든 권한을 부여하고, 그 외 사용자에게는 읽기 권한만 부여하는 권한 클래스입니다.
    """

    def has_permission(self, request, view):
        """
        요청이 읽기 권한을 요구하는 경우 모든 사용자에게 허용하고,
        쓰기 권한은 관리자만 사용할 수 있도록 제한합니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.

        Returns:
            bool: 읽기 요청이면 True, 관리자이면 True, 아니면 False.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsEnrolledOrAdmin(permissions.BasePermission):
    """
    관리자이거나 해당 코스에 등록된 사용자에게만 권한을 부여하는 권한 클래스입니다.
    """

    def has_object_permission(self, request, view, obj):
        """
        객체에 대한 접근 권한을 확인합니다. 관리자는 항상 허용되며,
        사용자는 해당 강의에 등록된 경우에만 접근 가능합니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.
            obj (Model): 접근하려는 객체.

        Returns:
            bool: 관리자인지 또는 해당 강의에 등록된 사용자인지 여부.
        """
        if request.user and request.user.is_staff:
            return True

        if hasattr(obj, "enrollments"):
            return obj.enrollments.filter(user=request.user, status="active").exists()

        if hasattr(obj, "major_category"):
            return obj.major_category.enrollments.filter(
                user=request.user, status="active"
            ).exists()

        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    객체의 소유자이거나 관리자일 경우에만 권한을 부여하는 권한 클래스입니다.
    """

    def has_object_permission(self, request, view, obj):
        """
        객체에 대한 접근 권한을 확인합니다. 객체의 소유자이거나 관리자일 경우에만 허용합니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.
            obj (Model): 접근하려는 객체.

        Returns:
            bool: 객체 소유자이거나 관리자인지 여부.
        """
        return obj.user == request.user or request.user.is_staff


class AllowAnyForList(permissions.BasePermission):
    """
    GET 요청(리스트 조회)은 모든 사용자에게 허용하고,
    POST 요청(생성)은 관리자에게만 허용하는 권한 클래스입니다.
    """

    def has_permission(self, request, view):
        """
        GET 요청은 모든 사용자에게 허용하고, POST 요청은 관리자에게만 허용합니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.

        Returns:
            bool: GET 요청이면 True, POST 요청이면 관리자 여부에 따라 True/False.
        """
        if request.method == "GET":
            return True
        return request.user and request.user.is_staff


class IsAdminOrManagerOnly(permissions.BasePermission):
    """
    관리자 또는 매니저만 접근할 수 있는 권한 클래스입니다.
    """

    def has_permission(self, request, view):
        """
        관리자가 아니면 접근을 제한합니다. 사용자 역할이 admin 또는 manager일 경우에만 접근을 허용합니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.

        Returns:
            bool: 사용자 역할이 admin 또는 manager인지 여부.
        """
        return request.user.is_authenticated and request.user.role in ["admin", "manager"]

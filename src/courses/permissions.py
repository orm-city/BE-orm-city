from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    관리자 사용자에게는 모든 권한을 부여하고, 그 외 사용자에게는 읽기 권한만 부여합니다.
    """

    def has_permission(self, request, view):
        # 읽기 권한은 모든 요청에 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        # 쓰기 권한은 관리자에게만 허용
        return request.user and request.user.is_staff


class IsEnrolledOrAdmin(permissions.BasePermission):
    """
    관리자이거나 해당 코스에 등록된 사용자에게 권한을 부여합니다.
    """

    def has_object_permission(self, request, view, obj):
        # 관리자는 모든 권한 가짐
        if request.user and request.user.is_staff:
            return True
        # 등록된 사용자 확인 (obj가 MajorCategory인 경우)
        if hasattr(obj, "enrollments"):
            return obj.enrollments.filter(user=request.user, status="active").exists()
        # MinorCategory의 경우, 연관된 MajorCategory 확인
        if hasattr(obj, "major_category"):
            return obj.major_category.enrollments.filter(
                user=request.user, status="active"
            ).exists()
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    객체의 소유자이거나 관리자인 경우에만 권한을 부여합니다.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class AllowAnyForList(permissions.BasePermission):
    """
    GET 요청(리스트 조회)은 모든 사용자에게 허용하고,
    POST 요청(생성)은 관리자에게만 허용합니다.
    """

    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return request.user and request.user.is_staff


class IsAdminOrManagerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            "admin",
            "manager",
        ]

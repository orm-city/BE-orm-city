from rest_framework.permissions import BasePermission


class IsAuthenticatedAndAllowed(BasePermission):
    """
    회원 또는 관리자만 접근을 허용하는 권한 클래스
    """

    def has_permission(self, request, view):
        # 사용자가 인증되었는지 확인
        if not request.user.is_authenticated:
            return False

        # 사용자의 역할이 학생, 관리자, 어드민 중 하나인지 확인
        allowed_roles = ["student", "manager", "admin"]
        return request.user.role in allowed_roles

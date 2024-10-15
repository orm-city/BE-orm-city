from rest_framework.permissions import BasePermission


class IsAuthenticatedAndAllowed(BasePermission):
    """
    인증된 사용자 중 학생, 관리자 또는 어드민 역할을 가진 사용자에게만 접근을 허용하는 권한 클래스입니다.
    
    메서드:
        has_permission(request, view): 사용자가 인증되었는지와 허용된 역할을 가지고 있는지 확인합니다.
    """

    def has_permission(self, request, view):
        """
        요청 사용자가 인증되고 허용된 역할을 가지고 있는지 확인합니다.
        
        Args:
            request: 현재 HTTP 요청 객체.
            view: 접근하려는 뷰.
        
        Returns:
            bool: 사용자가 인증되고 허용된 역할을 가지고 있을 경우 True, 그렇지 않을 경우 False.
        """
        # 사용자가 인증되었는지 확인
        if not request.user.is_authenticated:
            return False

        # 사용자의 역할이 학생, 관리자, 어드민 중 하나인지 확인
        allowed_roles = ["student", "manager", "admin"]
        return request.user.role in allowed_roles

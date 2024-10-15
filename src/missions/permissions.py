from rest_framework import permissions
from courses.models import Enrollment


class IsActiveOrCompletedEnrollmentOrManagerAdmin(permissions.BasePermission):
    """
    미션 리스트 및 리트라이브에 사용할 권한 클래스.
    
    다음의 경우에 접근을 허용합니다:
    - 사용자의 Enrollment 객체의 상태가 'active' 또는 'completed'일 경우.
    - 사용자의 역할(role)이 'manager' 또는 'admin'일 경우.
    - 현재 접근하려는 Mission의 MinorCategory가 사용자가 등록한 MajorCategory에 속할 경우.
    """

    def get_minor_category(self, obj):
        """
        객체의 타입에 따라 MinorCategory를 동적으로 가져오는 메서드.

        Args:
            obj: 확인할 객체 (Mission 또는 Mission과 연결된 객체).

        Returns:
            MinorCategory: 객체에 연결된 MinorCategory를 반환.
        """
        # Mission 객체일 경우
        if hasattr(obj, "minor_category"):
            return obj.minor_category
        # Mission과 연결된 다른 객체일 경우 (예: MultipleChoiceQuestion)
        elif hasattr(obj, "mission") and hasattr(obj.mission, "minor_category"):
            return obj.mission.minor_category
        return None

    def has_object_permission(self, request, view, obj):
        """
        객체 수준의 권한을 결정하는 메서드.

        Args:
            request: 현재 요청 객체.
            view: 접근하려는 뷰.
            obj: 접근하려는 객체.

        Returns:
            bool: 접근 허가 여부.
        """
        # 관리자 또는 매니저 권한 확인
        if request.user.role in ["manager", "admin"]:
            return True

        # MinorCategory를 가져와 해당 MajorCategory에서 등록 여부 확인
        minor_category = self.get_minor_category(obj)
        if minor_category is None:
            return False

        major_category = minor_category.major_category
        enrollment = Enrollment.objects.filter(
            user=request.user, major_category=major_category
        ).first()

        # 등록 상태가 'active' 또는 'completed'이면 True 반환
        if enrollment and enrollment.status in ["active", "completed"]:
            return True

        return False


class IsManagerOrAdmin(permissions.BasePermission):
    """
    수정 권한을 부여하는 권한 클래스.
    
    사용자의 역할이 'manager' 또는 'admin'일 경우에만 접근을 허용합니다.
    """

    def has_permission(self, request, view):
        """
        접근 권한을 결정하는 메서드.

        Args:
            request: 현재 요청 객체.
            view: 접근하려는 뷰.

        Returns:
            bool: 사용자의 역할이 'manager' 또는 'admin'일 경우 True 반환.
        """
        return request.user.role in ["manager", "admin"]

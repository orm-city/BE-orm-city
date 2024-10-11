from rest_framework import permissions
from .models import Enrollment


class IsActiveOrCompletedEnrollmentOrManagerAdmin(permissions.BasePermission):
    """
    미션 리스트 및 리트라이브에 사용할 permission:
    - Enrollment 객체의 status가 'active' 또는 'completed'일 경우 허가.
    - CustomUser의 role이 'manager' 또는 'admin'일 경우 허가.
    - 현재 접근하려는 Mission의 MinorCategory에 속한 MajorCategory가 사용자의 Enrollment에 포함되어 있을 경우 허가.
    """

    def get_minor_category(self, obj):
        """
        객체 타입에 따라 MinorCategory를 동적으로 가져오는 메서드.
        Mission 객체인지, Mission과 연결된 다른 객체인지 확인 후 MinorCategory 반환.
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
        특정 Mission 객체 또는 Mission과 연결된 객체에 대한 권한을 결정.
        """
        if request.user.role in ["manager", "admin"]:
            return True

        minor_category = self.get_minor_category(obj)

        if minor_category is None:
            return False

        major_category = minor_category.major_category

        enrollment = Enrollment.objects.filter(
            user=request.user, major_category=major_category
        ).first()

        if enrollment and enrollment.status in ["active", "completed"]:
            return True

        return False


class IsManagerOrAdmin(permissions.BasePermission):
    """
    수정할 때 사용할 permission:
    - CustomUser의 role이 'manager' 또는 'admin'일 경우 허가.
    """

    def has_permission(self, request, view):
        # 사용자의 role이 'manager' 또는 'admin'일 경우 허가
        return request.user.role in ["manager", "admin"]

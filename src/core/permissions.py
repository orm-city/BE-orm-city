from rest_framework.permissions import BasePermission
from courses.models import Enrollment


class IsEnrolledInCourse(BasePermission):
    """
    사용자가 로그인하였으며, 해당 강의에 등록된 사람만 접근 가능
    """

    def has_permission(self, request, view):
        # 사용자가 로그인한 상태인지 확인
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 강의와 연관된 Video 객체를 사용하여 해당 강의에 사용자가 등록되었는지 확인
        try:
            enrollment = Enrollment.objects.get(  # noqa
                user=request.user, major_category=obj.major_category
            )
            return True
        except Enrollment.DoesNotExist:
            return False


class IsAdminUser(BasePermission):
    """
    사용자 역할이 'admin'인 경우에만 접근을 허용하는 권한 클래스
    """

    def has_permission(self, request, view):
        # 사용자가 로그인했는지 확인
        if not request.user or not request.user.is_authenticated:
            return False

        # 사용자의 role이 'admin'인지 확인
        return request.user.role == "admin"


class IsEnrolledOrAdmin(BasePermission):
    """
    사용자가 강의에 등록되었거나, admin 역할일 경우 접근을 허용하는 권한 클래스
    """

    def has_permission(self, request, view):
        # 사용자가 로그인한 상태인지 확인
        if not request.user or not request.user.is_authenticated:
            return False

        # 사용자가 admin 역할인지 확인
        if request.user.role == "admin":
            return True

        return True  # 이후에 객체 수준에서 추가 확인

    def has_object_permission(self, request, view, obj):
        # 사용자가 admin 역할인지 확인
        if request.user.role == "admin":
            return True

        # 사용자가 해당 강의에 등록되었는지 확인
        try:
            enrollment = Enrollment.objects.get(  # noqa
                user=request.user, major_category=obj.minor_category.major_category
            )
            return True
        except Enrollment.DoesNotExist:
            return False
        except AttributeError:
            # minor_category가 없거나 잘못된 접근일 경우 처리
            return False

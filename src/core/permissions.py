from rest_framework.permissions import BasePermission

from courses.models import Enrollment


class IsEnrolledInCourse(BasePermission):
    """
    사용자가 로그인하였으며, 해당 강의에 등록된 사람만 접근할 수 있는 권한 클래스입니다.
    """

    def has_permission(self, request, view):
        """
        사용자가 로그인한 상태인지 확인하는 메서드입니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.

        Returns:
            bool: 사용자가 인증되었는지 여부.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        사용자가 해당 강의에 등록되었는지 확인하는 메서드입니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.
            obj (Model): 접근하려는 객체 (일반적으로 Video 객체).

        Returns:
            bool: 사용자가 해당 강의에 등록되었는지 여부.
        """
        try:
            enrollment = Enrollment.objects.get(
                user=request.user, major_category=obj.major_category
            )
            return enrollment
        except Enrollment.DoesNotExist:
            return False


class IsAdminUser(BasePermission):
    """
    사용자의 역할이 'admin'인 경우에만 접근을 허용하는 권한 클래스입니다.
    """

    def has_permission(self, request, view):
        """
        사용자가 관리자(admin)인지 확인하는 메서드입니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.

        Returns:
            bool: 사용자가 관리자(admin)인지 여부.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == "admin"


class IsEnrolledOrAdmin(BasePermission):
    """
    사용자가 해당 강의에 등록되었거나, 관리자(admin)인 경우에만 접근을 허용하는 권한 클래스입니다.
    """

    def has_permission(self, request, view):
        """
        사용자가 인증되었는지, 관리자(admin)인지 확인하는 메서드입니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.

        Returns:
            bool: 사용자가 인증되었는지 여부.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == "admin":
            return True
        return True  # 이후 객체 수준에서 확인

    def has_object_permission(self, request, view, obj):
        """
        사용자가 해당 강의에 등록되었는지 또는 관리자(admin)인지 확인하는 메서드입니다.

        Args:
            request (HttpRequest): 요청 객체.
            view (View): 요청된 뷰 객체.
            obj (Model): 접근하려는 객체 (일반적으로 Video 객체).

        Returns:
            bool: 사용자가 관리자이거나 해당 강의에 등록되었는지 여부.
        """
        if request.user.role == "admin":
            return True

        try:
            enrollment = Enrollment.objects.get(
                user=request.user, major_category=obj.minor_category.major_category
            )
            return enrollment
        except Enrollment.DoesNotExist:
            return False
        except AttributeError:
            return False  # minor_category가 없거나 잘못된 접근일 경우

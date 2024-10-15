from rest_framework.permissions import BasePermission
from courses.models import MajorCategory, MinorCategory
from progress.models import UserProgress
from videos.models import Video


class IsCertificateOwner(BasePermission):
    """
    사용자가 발급받은 인증서만 확인할 수 있도록 하는 권한 클래스입니다.
    
    MinorCategory 또는 MajorCategory에 속한 모든 동영상을 완료한 경우에만 인증서에 접근할 수 있습니다.
    """

    def has_permission(self, request, view):
        """
        사용자가 인증서를 확인할 수 있는 권한이 있는지 검증합니다.

        사용자가 특정 소분류(MinorCategory) 또는 대분류(MajorCategory) 과정의 모든 동영상을 완료한 경우에만 접근을 허용합니다.

        Args:
            request (Request): HTTP 요청 객체.
            view (View): 요청한 뷰 객체.

        Returns:
            bool: 사용자가 인증서에 접근할 수 있는지 여부.
        """
        course_type = view.kwargs.get("course_type")
        course_id = view.kwargs.get("course_id")
        user = request.user

        if course_type == "minor":
            # 소분류 과정에서 사용자가 모든 동영상을 완료했는지 확인
            try:
                minor_category = MinorCategory.objects.get(id=course_id)
                videos = Video.objects.filter(minor_category=minor_category)
                
                # 사용자가 모든 동영상을 완료했는지 확인
                completed_videos = UserProgress.objects.filter(
                    user=user, video__in=videos, is_completed=True
                ).count()
                return completed_videos == videos.count()
            except MinorCategory.DoesNotExist:
                return False

        elif course_type == "major":
            # 대분류 과정에서 사용자가 모든 동영상을 완료했는지 확인
            try:
                major_category = MajorCategory.objects.get(id=course_id)
                videos = Video.objects.filter(
                    minor_category__major_category=major_category
                )
                
                # 사용자가 모든 동영상을 완료했는지 확인
                completed_videos = UserProgress.objects.filter(
                    user=user, video__in=videos, is_completed=True
                ).count()
                return completed_videos == videos.count()
            except MajorCategory.DoesNotExist:
                return False

        return False

from rest_framework.permissions import BasePermission

from courses.models import MajorCategory, MinorCategory
from progress.models import UserProgress
from videos.models import Video


class IsCertificateOwner(BasePermission):
    """
    사용자가 발급받은 인증서만 확인할 수 있도록 하는 권한.
    MinorCategory 또는 MajorCategory에 포함된 모든 동영상을 완료한 경우에만 접근 허용.
    """

    def has_permission(self, request, view):
        course_type = view.kwargs.get("course_type")
        course_id = view.kwargs.get("course_id")
        user = request.user

        if course_type == "minor":
            # 소분류 과정에서 사용자가 모든 동영상을 완료했는지 확인
            try:
                minor_category = MinorCategory.objects.get(id=course_id)
                videos = Video.objects.filter(minor_category=minor_category)
                # 모든 동영상이 완료되었는지 확인
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
                # 모든 동영상이 완료되었는지 확인
                completed_videos = UserProgress.objects.filter(
                    user=user, video__in=videos, is_completed=True
                ).count()
                return completed_videos == videos.count()
            except MajorCategory.DoesNotExist:
                return False

        return False

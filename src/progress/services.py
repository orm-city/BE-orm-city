from django.utils import timezone
from django.db.models import Avg
from django.db import transaction


class UserProgressService:
    """
    유저의 학습 진행률을 처리하는 서비스 클래스.

    이 클래스는 학습 진행률 업데이트, 리셋, 전체 진행률 및 카테고리별 진행률 계산 기능을 제공합니다.
    """

    @staticmethod
    @transaction.atomic
    def update_progress(user_progress, progress_percent, additional_time, last_position):
        """
        유저의 학습 진행률을 업데이트하는 메서드.

        Args:
            user_progress (UserProgress): 업데이트할 진행률 객체.
            progress_percent (float): 업데이트할 진행 퍼센트 (최대 100).
            additional_time (timedelta): 추가된 시청 시간.
            last_position (int): 마지막 시청 위치.

        Returns:
            UserProgress: 업데이트된 진행률 객체.
        """
        user_progress.progress_percent = min(progress_percent, 100)
        user_progress.time_spent += additional_time
        user_progress.last_position = last_position
        user_progress.last_accessed = timezone.now()

        if progress_percent >= 95:
            user_progress.is_completed = True

        user_progress.save()
        return user_progress

    @staticmethod
    @transaction.atomic
    def reset_progress(user_progress):
        """
        유저의 학습 진행률을 리셋하는 메서드.

        Args:
            user_progress (UserProgress): 리셋할 진행률 객체.

        Returns:
            UserProgress: 리셋된 진행률 객체.
        """
        user_progress.progress_percent = 0
        user_progress.time_spent = timezone.timedelta()
        user_progress.last_position = 0
        user_progress.is_completed = False
        user_progress.save()
        return user_progress

    @staticmethod
    def calculate_overall_progress(user):
        """
        유저의 전체 학습 진행률을 계산하는 메서드.

        Args:
            user (CustomUser): 학습 진행률을 계산할 사용자.

        Returns:
            float: 전체 학습 진행률 (소수점 둘째 자리까지 반올림).
        """
        from .models import Enrollment, UserProgress

        enrollments = Enrollment.objects.filter(user=user, status="active")
        if not enrollments:
            return 0

        overall_progress = (
            UserProgress.objects.filter(enrollment__in=enrollments).aggregate(
                Avg("progress_percent")
            )["progress_percent__avg"]
            or 0
        )

        return round(overall_progress, 2)

    @staticmethod
    def get_category_progress(user, major_category):
        """
        특정 대분류(카테고리)의 학습 진행률을 계산하는 메서드.

        Args:
            user (CustomUser): 학습 진행률을 계산할 사용자.
            major_category (MajorCategory): 계산할 대분류(카테고리).

        Returns:
            float: 해당 카테고리의 학습 진행률 (소수점 둘째 자리까지 반올림).
        """
        from .models import Enrollment, UserProgress
        from videos.models import Video

        enrollment = Enrollment.objects.filter(
            user=user, major_category=major_category, status="active"
        ).first()

        if not enrollment:
            return 0

        videos = Video.objects.filter(minor_category__major_category=major_category)
        progress = (
            UserProgress.objects.filter(
                user=user, video__in=videos, enrollment=enrollment
            ).aggregate(Avg("progress_percent"))["progress_percent__avg"]
            or 0
        )

        return round(progress, 2)

from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce


class ProgressService:
    """
    학습 진행률을 계산하는 서비스 클래스입니다.
    """

    @staticmethod
    def calculate_category_progress(category):
        """
        MinorCategory에서 동영상의 총 진행률을 계산합니다.

        해당 소분류의 모든 동영상에 대해 진행률과 비디오 길이를 고려한 가중 평균을 계산합니다.

        Args:
            category (MinorCategory): 진행률을 계산할 소분류 객체.

        Returns:
            float: 소분류에 대한 총 진행률 (0 ~ 1).
        """
        video_stats = category.videos.annotate(
            weighted_progress=ExpressionWrapper(
                F("progresses__progress_percent") * F("duration"),
                output_field=FloatField(),
            )
        ).aggregate(
            total_progress=Sum("weighted_progress"),
            total_video_duration=Sum("duration"),
        )

        total_video_duration = (
            video_stats["total_video_duration"].total_seconds()
            if video_stats["total_video_duration"]
            else 0
        )
        if total_video_duration == 0:
            return 0

        total_progress = (
            video_stats["total_progress"].total_seconds()
            if video_stats["total_progress"]
            else 0
        )
        return total_progress / total_video_duration

    @staticmethod
    def calculate_major_category_progress(major_category):
        """
        MajorCategory의 진행률을 계산합니다.
        각 MinorCategory의 진행률을 합산하여 가중 평균을 구합니다.

        Args:
            major_category (MajorCategory): 진행률을 계산할 대분류 객체.

        Returns:
            float: 대분류에 대한 총 진행률 (0 ~ 1).
        """
        minor_categories = major_category.minor_categories.annotate(
            total_duration=Coalesce(Sum("videos__duration"), 0),
            weighted_progress=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("videos__progresses__progress_percent")
                        * F("videos__duration"),
                        output_field=FloatField(),
                    )
                ),
                0,
            ),
        ).aggregate(
            total_minor_duration=Sum("total_duration"),
            total_progress=Sum("weighted_progress"),
        )

        total_minor_duration = (
            minor_categories["total_minor_duration"].total_seconds()
            if minor_categories["total_minor_duration"]
            else 0
        )
        if total_minor_duration == 0:
            return 0

        total_progress = (
            minor_categories["total_progress"].total_seconds()
            if minor_categories["total_progress"]
            else 0
        )
        return total_progress / total_minor_duration

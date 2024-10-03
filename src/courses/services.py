from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce


class ProgressService:
    @staticmethod
    def calculate_category_progress(category):
        """
        MinorCategory에서 동영상의 총 진행률을 계산.
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

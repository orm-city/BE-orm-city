from django.utils import timezone


class UserProgressService:
    @staticmethod
    def calculate_progress(user_progress):
        """진도율을 계산하여 반환하는 헬퍼 메서드"""
        if user_progress.video.duration.total_seconds() == 0:
            return 0
        return (
            user_progress.time_spent.total_seconds()
            / user_progress.video.duration.total_seconds()
        ) * 100

    @staticmethod
    def update_progress(user_progress, new_percent, additional_time, last_position):
        user_progress.time_spent += additional_time
        progress = min(
            new_percent, min(100, UserProgressService.calculate_progress(user_progress))
        )
        user_progress.progress_percent = progress
        user_progress.last_accessed = timezone.now()
        user_progress.last_position = last_position
        if user_progress.progress_percent >= 95:
            user_progress.is_completed = True
        user_progress.save()

    @staticmethod
    def reset_progress(user_progress):
        user_progress.is_completed = False
        user_progress.progress_percent = 0
        user_progress.time_spent = timezone.timedelta()
        user_progress.last_position = 0
        user_progress.save()

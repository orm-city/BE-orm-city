from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta

from accounts.models import CustomUser
from courses.models import MajorCategory, Enrollment
from payment.models import Payment
from .models import UserLearningRecord, UserVideoProgress, ExpirationNotification
from missions.models import MissionSubmission


class DashboardService:
    @staticmethod
    def get_dashboard_summary():
        total_students = CustomUser.objects.filter(role="student").count()
        total_courses = MajorCategory.objects.count()
        total_revenue = (
            Payment.objects.aggregate(total=Sum("total_amount"))["total"] or 0
        )
        avg_completion_rate = (
            Enrollment.objects.filter(status="completed").count()
            / Enrollment.objects.count()
            * 100
            if Enrollment.objects.exists()
            else 0
        )

        return {
            "total_students": total_students,
            "total_courses": total_courses,
            "total_revenue": total_revenue,
            "avg_completion_rate": avg_completion_rate,
        }

    @staticmethod
    def get_student_dashboard(user):
        learning_record = (
            UserLearningRecord.objects.filter(user=user).order_by("-date").first()
        )
        video_progress = (
            UserVideoProgress.objects.filter(user_progress__user=user)
            .order_by("-date")
            .first()
        )

        enrollments = Enrollment.objects.filter(user=user)
        active_courses = enrollments.filter(status="active").count()
        completed_courses = enrollments.filter(status="completed").count()

        total_study_time = (
            UserLearningRecord.objects.filter(user=user).aggregate(
                total=Sum("total_study_time")
            )["total"]
            or timedelta()
        )

        last_30_days = timezone.now() - timedelta(days=30)
        avg_daily_study_time = (
            UserLearningRecord.objects.filter(
                user=user, date__gte=last_30_days
            ).aggregate(avg=Avg("total_study_time"))["avg"]
            or timedelta()
        )

        next_expiration = (
            ExpirationNotification.objects.filter(user=user, is_sent=False)
            .order_by("notification_date")
            .first()
        )

        recent_missions = MissionSubmission.objects.filter(user=user).order_by(
            "-submitted_at"
        )[:5]

        return {
            "learning_record": learning_record,
            "video_progress": video_progress,
            "active_courses": active_courses,
            "completed_courses": completed_courses,
            "total_study_time": total_study_time,
            "average_daily_study_time": avg_daily_study_time,
            "next_expiration": next_expiration,
            "recent_missions": recent_missions,
        }

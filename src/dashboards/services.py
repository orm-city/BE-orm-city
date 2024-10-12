from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from accounts.models import CustomUser
from courses.models import MajorCategory, Enrollment
from payment.models import Payment
from .models import (
    UserLearningRecord,
    UserVideoProgress,
    ExpirationNotification,
    DailyVisit,
)
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
            "next_expiration": next_expiration,
            "recent_missions": recent_missions,
        }

    @staticmethod
    def get_daily_visits(days=7):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)
        daily_visits = DailyVisit.objects.filter(date__range=[start_date, end_date])

        # 모든 날짜에 대해 데이터 생성 (방문이 없는 날도 0으로 표시)
        all_dates = {
            start_date + timedelta(days=i): {
                "date": start_date + timedelta(days=i),
                "student_unique_visitors": 0,
                "student_total_views": 0,
            }
            for i in range(days)
        }

        for visit in daily_visits:
            all_dates[visit.date] = {
                "date": visit.date,
                "student_unique_visitors": visit.student_unique_visitors,
                "student_total_views": visit.student_total_views,
            }

        return list(all_dates.values())

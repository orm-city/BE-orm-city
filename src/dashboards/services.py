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
    """
    대시보드 관련 서비스를 제공하는 클래스입니다.

    이 클래스는 학생 수, 강의 수, 총 수익, 학습 진행률 등과 같은 대시보드 정보를 처리하는 여러 메서드를 포함합니다.
    """

    @staticmethod
    def get_dashboard_summary():
        """
        전체 대시보드 요약 정보를 반환합니다.

        Returns:
            dict: 총 학생 수, 총 강의 수, 총 수익, 평균 완료율을 포함한 대시보드 요약 정보.
        """
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
        """
        특정 학생에 대한 대시보드 정보를 반환합니다.

        Args:
            user (CustomUser): 대시보드 정보를 조회할 사용자 객체.

        Returns:
            dict: 학습 기록, 비디오 진행 상황, 활성/완료된 강의 수, 다음 만료 알림, 최근 미션 제출 정보를 포함한 대시보드 정보.
        """
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
        """
        최근 N일간의 일일 방문 기록을 반환합니다.

        Args:
            days (int): 조회할 일 수. 기본값은 7일입니다.

        Returns:
            list: 날짜별로 방문자 수와 조회 수를 포함한 일일 방문 기록 목록.
        """
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

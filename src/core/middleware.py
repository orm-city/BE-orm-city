import json

from django.utils import timezone
from django.db.models import F

from dashboards.models import DailyVisit


class VisitTrackerMiddleware:
    """
    방문 추적을 위한 미들웨어 클래스입니다.

    사용자의 IP를 기반으로 매일 한 번의 방문만을 기록하며,
    해당 날짜의 고유 방문자 수와 총 조회수를 업데이트합니다.
    """

    def __init__(self, get_response):
        """
        미들웨어 초기화 메서드입니다.

        Args:
            get_response (function): 다음 미들웨어 또는 뷰를 호출하는 함수.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        미들웨어의 핵심 로직으로, 요청을 처리하고 방문 기록을 업데이트합니다.

        Args:
            request (HttpRequest): 들어오는 요청 객체.

        Returns:
            HttpResponse: 처리된 응답 객체.
        """
        if not request.session.get("visit_tracked_today"):
            self._track_visit(request)
            request.session["visit_tracked_today"] = True
            request.session["visit_tracked_date"] = timezone.now().date().isoformat()
        else:
            tracked_date = request.session.get("visit_tracked_date")
            if tracked_date != timezone.now().date().isoformat():
                self._track_visit(request)
                request.session["visit_tracked_today"] = True
                request.session["visit_tracked_date"] = (
                    timezone.now().date().isoformat()
                )

        response = self.get_response(request)
        return response

    def _track_visit(self, request):
        """
        방문 기록을 추적하고 데이터베이스에 고유 방문자와 조회수를 업데이트합니다.

        Args:
            request (HttpRequest): 들어오는 요청 객체.
        """
        today = timezone.now().date()
        ip_address = self._get_client_ip(request)

        daily_visit, created = DailyVisit.objects.get_or_create(date=today)

        unique_ips = daily_visit.get_unique_ips()
        if ip_address not in unique_ips:
            DailyVisit.objects.filter(id=daily_visit.id).update(
                student_unique_visitors=F("student_unique_visitors") + 1,
                unique_ips=json.dumps(unique_ips + [ip_address]),
            )

        DailyVisit.objects.filter(id=daily_visit.id).update(
            student_total_views=F("student_total_views") + 1
        )

    def _get_client_ip(self, request):
        """
        클라이언트의 IP 주소를 추출합니다.

        Args:
            request (HttpRequest): 들어오는 요청 객체.

        Returns:
            str: 클라이언트의 IP 주소.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

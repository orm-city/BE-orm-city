from django.utils import timezone
from django.db.models import F
from dashboards.models import DailyVisit
import json


class VisitTrackerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

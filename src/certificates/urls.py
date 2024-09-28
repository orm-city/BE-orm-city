from django.urls import path
from .views import CertificatePreviewView, CertificateDownloadView

urlpatterns = [
    path(
        "preview/<str:course_type>/<int:course_id>/",
        CertificatePreviewView.as_view(),
        name="certificate_preview",
    ),
    path(
        "download/<str:course_type>/<int:course_id>/",
        CertificateDownloadView.as_view(),
        name="certificate_download",
    ),
]

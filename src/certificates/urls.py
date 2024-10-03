from django.urls import path
from .views import (
    CertificatePreviewAPIView,
    CertificateDownloadAPIView,
    AvailableCertificatesAPIView,
    VerifyCertificateAPIView,
)

urlpatterns = [
    path(
        "preview/<str:course_type>/<int:course_id>/",
        CertificatePreviewAPIView.as_view(),
        name="certificate_preview",
    ),
    path(
        "download/<str:course_type>/<int:course_id>/",
        CertificateDownloadAPIView.as_view(),
        name="certificate_download",
    ),
    path("", AvailableCertificatesAPIView.as_view(), name="available_certificates"),
    path(
        "verify/<uuid:certificate_id>/",
        VerifyCertificateAPIView.as_view(),
        name="certificate_verify",
    ),
]

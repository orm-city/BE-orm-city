from django.urls import path
from .views import CertificatePreviewAPIView, CertificateDownloadAPIView

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
]

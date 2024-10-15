# urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("certificates/", include("certificates.urls")),
    path("courses/", include("courses.urls")),
    # path("dashboards/", include("dashboards.urls")),
    path("missions/", include("missions.urls")),
    path("payment/", include("payment.urls")),
    path("progress/", include("progress.urls")),
    path("videos/", include("videos.urls")),
]

# drf_spectacular
urlpatterns += [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]


if settings.ADMIN_ENABLED:
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]

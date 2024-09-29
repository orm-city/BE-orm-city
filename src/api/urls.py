from django.urls import path, include
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
    # path("missions/", include("missions.urls")),
    path("payment/", include("payment.urls")),
    # path("progress/", include("progress.urls")),
    path("videos/", include("videos.urls")),
]

# drf_spectacular
urlpatterns += [
    # YOUR PATTERNS
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
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

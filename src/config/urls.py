from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("api/", include("missions.urls")),  # 미션 url 추가
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/certificates/", include("certificates.urls")),
    path("api/v1/courses/", include("courses.urls")),
    path("api/v1/payment/", include("payment.urls")),
    path("api/v1/videos/", include("videos.urls")),
]

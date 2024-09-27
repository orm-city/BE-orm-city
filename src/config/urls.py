from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/videos/", include("videos.urls")),
    path("api/v1/courses/", include("courses.urls")),
    path("api/v1/payment/", include("payment.urls")),
]

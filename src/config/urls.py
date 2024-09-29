# https://docs.djangoproject.com/en/5.1/topics/http/urls/
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("api/", include("api.urls")),
]

if settings.ADMIN_ENABLED is True:
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]

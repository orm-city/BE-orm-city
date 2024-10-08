from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MajorCategoryViewSet, MinorCategoryViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r"major-categories", MajorCategoryViewSet, basename="majorcategory")
router.register(r"minor-categories", MinorCategoryViewSet, basename="minorcategory")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")

# EnrollmentViewSet의 custom action을 명시적으로 등록
enrollment_complete = EnrollmentViewSet.as_view({"post": "complete_enrollment"})

urlpatterns = [
    path("", include(router.urls)),
    path(
        "enrollments/<int:pk>/complete/",
        enrollment_complete,
        name="enrollment-complete-enrollment",
    ),
]

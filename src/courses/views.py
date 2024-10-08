from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import MajorCategory, MinorCategory, Enrollment
from .serializers import (
    MajorCategorySerializer,
    MinorCategorySerializer,
    EnrollmentSerializer,
)
from videos.models import Video
from .permissions import (
    IsAdminOrReadOnly,
    IsEnrolledOrAdmin,
    AllowAnyForList,
    IsOwnerOrAdmin,
    IsAdminOrManagerOnly,
)
from drf_spectacular.utils import extend_schema_view, extend_schema


# MajorCategoryViewSet with @extend_schema_view
@extend_schema_view(
    list=extend_schema(tags=["courses"]),
    retrieve=extend_schema(tags=["courses"]),
    create=extend_schema(tags=["courses"]),
    update=extend_schema(tags=["courses"]),
    partial_update=extend_schema(tags=["courses"]),
    destroy=extend_schema(tags=["courses"]),
    details=extend_schema(tags=["courses"]),
)
class MajorCategoryViewSet(viewsets.ModelViewSet):
    queryset = MajorCategory.objects.all()
    serializer_class = MajorCategorySerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAnyForList]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminOrReadOnly]
        else:
            permission_classes = [IsEnrolledOrAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["get"])
    def details(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        video_stats = Video.objects.filter(
            minor_category__major_category=instance
        ).aggregate(total_count=Count("id"), total_duration=Sum("duration"))

        data["total_video_count"] = video_stats["total_count"]
        data["total_video_duration"] = video_stats["total_duration"]

        return Response(data)


# MinorCategoryViewSet with @extend_schema_view
@extend_schema_view(
    list=extend_schema(tags=["courses"]),
    retrieve=extend_schema(tags=["courses"]),
    create=extend_schema(tags=["courses"]),
    update=extend_schema(tags=["courses"]),
    partial_update=extend_schema(tags=["courses"]),
    destroy=extend_schema(tags=["courses"]),
)
class MinorCategoryViewSet(viewsets.ModelViewSet):
    queryset = MinorCategory.objects.all()
    serializer_class = MinorCategorySerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAnyForList]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminOrReadOnly]
        else:
            permission_classes = [IsEnrolledOrAdmin]
        return [permission() for permission in permission_classes]


# EnrollmentViewSet with @extend_schema_view
@extend_schema_view(
    list=extend_schema(tags=["courses"]),
    retrieve=extend_schema(tags=["courses"]),
    create=extend_schema(tags=["courses"]),
    update=extend_schema(tags=["courses"]),
    partial_update=extend_schema(tags=["courses"]),
    destroy=extend_schema(tags=["courses"]),
    active_enrollments=extend_schema(tags=["courses"]),
    complete_enrollment=extend_schema(tags=["courses"]),
)
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAdminOrReadOnly]
        elif self.action == "complete_enrollment":
            permission_classes = [IsAdminOrManagerOnly]
        else:
            permission_classes = [IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.role == "manager":
            return Enrollment.objects.all()
        return Enrollment.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if request.user.role != "student":
            return Response(
                {"error": "Only students can enroll in courses"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if Enrollment.objects.filter(
            user=request.user, major_category_id=request.data.get("major_category")
        ).exists():
            return Response(
                {"error": "You are already enrolled in this course"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_create(serializer)
        except MajorCategory.DoesNotExist:
            return Response(
                {"error": "Invalid major category"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        major_category_id = self.request.data.get("major_category")
        major_category = MajorCategory.objects.get(pk=major_category_id)
        enrollment_date = timezone.now()
        expiry_date = enrollment_date + relativedelta(years=2)
        serializer.save(
            user=self.request.user,
            major_category=major_category,
            enrollment_date=enrollment_date,
            expiry_date=expiry_date,
        )

    @action(detail=False, methods=["get"])
    def active_enrollments(self, request):
        active_enrollments = self.get_queryset().filter(status="active")
        serializer = self.get_serializer(active_enrollments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def complete_enrollment(self, request, pk=None):
        enrollment = self.get_object()
        if enrollment.status == "active":
            enrollment.status = "completed"
            enrollment.save()
            return Response({"status": "enrollment completed"})
        return Response(
            {"status": "enrollment cannot be completed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

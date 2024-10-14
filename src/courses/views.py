from django.db.models import Sum, Count
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dateutil.relativedelta import relativedelta
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import MajorCategory, MinorCategory, Enrollment
from .schema import major_category_schemas, minor_category_schemas, enrollment_schemas  
from .serializers import MajorCategorySerializer, MinorCategorySerializer, EnrollmentSerializer
from videos.models import Video
from .permissions import (
    IsAdminOrReadOnly,
    IsEnrolledOrAdmin,
    AllowAnyForList,
    IsOwnerOrAdmin,
    IsAdminOrManagerOnly,
)


@extend_schema_view(**major_category_schemas)  
class MajorCategoryViewSet(viewsets.ModelViewSet):
    """
    MajorCategory 모델을 위한 ViewSet 클래스.

    이 클래스는 MajorCategory의 CRUD 작업과 추가 기능을 제공합니다.
    사용자의 권한에 따라 접근이 제한됩니다.

    Attributes:
        queryset (QuerySet): MajorCategory 모델에 대한 QuerySet.
        serializer_class (Serializer): MajorCategorySerializer 클래스.
    """

    queryset = MajorCategory.objects.all()
    serializer_class = MajorCategorySerializer

    def get_permissions(self):
        """
        요청하는 액션에 따라 권한을 설정합니다.

        Returns:
            list: 권한 클래스 목록.
        """
        if self.action == "list":
            permission_classes = [AllowAnyForList]
        elif self.action == "retrieve":
            permission_classes = [IsAuthenticated]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminOrReadOnly]
        else:
            permission_classes = [IsEnrolledOrAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["get"])
    def details(self, request, pk=None):
        """
        MajorCategory의 세부 정보를 반환합니다.

        Args:
            request (HttpRequest): 요청 객체.
            pk (int): MajorCategory의 기본 키.

        Returns:
            Response: MajorCategory의 세부 정보와 비디오 통계 정보를 반환.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        video_stats = Video.objects.filter(
            minor_category__major_category=instance
        ).aggregate(total_count=Count("id"), total_duration=Sum("duration"))

        data["total_video_count"] = video_stats["total_count"]
        data["total_video_duration"] = video_stats["total_duration"]

        return Response(data)


@extend_schema_view(**minor_category_schemas)  
class MinorCategoryViewSet(viewsets.ModelViewSet):
    """
    MinorCategory 모델을 위한 ViewSet 클래스.

    이 클래스는 MinorCategory의 CRUD 작업과 추가 기능을 제공합니다.
    사용자의 권한에 따라 접근이 제한됩니다.

    Attributes:
        queryset (QuerySet): MinorCategory 모델에 대한 QuerySet.
        serializer_class (Serializer): MinorCategorySerializer 클래스.
    """

    queryset = MinorCategory.objects.all()
    serializer_class = MinorCategorySerializer

    def get_permissions(self):
        """
        요청하는 액션에 따라 권한을 설정합니다.

        Returns:
            list: 권한 클래스 목록.
        """
        if self.action == "list":
            permission_classes = [AllowAnyForList]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminOrReadOnly]
        else:
            permission_classes = [IsEnrolledOrAdmin]
        return [permission() for permission in permission_classes]

    def get_major_category_queryset(self, major_category_id):
        """
        특정 MajorCategory에 속한 MinorCategory 목록을 반환합니다.

        Args:
            major_category_id (int): MajorCategory의 기본 키.

        Returns:
            QuerySet: 필터링된 MinorCategory 목록.
        """
        return self.queryset.filter(major_category_id=major_category_id).order_by("order")

    def list(self, request, *args, **kwargs):
        """
        MinorCategory 목록을 반환합니다.

        Args:
            request (HttpRequest): 요청 객체.

        Returns:
            Response: 필터링된 MinorCategory 목록.
        """
        major_category_id = request.query_params.get("major_category_id")
        if major_category_id:
            queryset = self.get_major_category_queryset(major_category_id)
        else:
            queryset = self.queryset
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_major_category(self, request, major_id=None):
        """
        특정 MajorCategory에 속한 MinorCategory 목록을 반환합니다.

        Args:
            request (HttpRequest): 요청 객체.
            major_id (int, optional): MajorCategory의 기본 키.

        Returns:
            Response: 필터링된 MinorCategory 목록.
        """
        if major_id is None:
            return Response({"error": "major_category_id is required"}, status=400)
        queryset = self.get_major_category_queryset(major_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(**enrollment_schemas) 
class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    Enrollment 모델을 위한 ViewSet 클래스.

    이 클래스는 수강 신청의 CRUD 작업과 추가 기능을 제공합니다.
    사용자의 권한에 따라 접근이 제한됩니다.

    Attributes:
        queryset (QuerySet): Enrollment 모델에 대한 QuerySet.
        serializer_class (Serializer): EnrollmentSerializer 클래스.
    """

    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_permissions(self):
        """
        요청하는 액션에 따라 권한을 설정합니다.

        Returns:
            list: 권한 클래스 목록.
        """
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
        """
        현재 사용자의 권한에 따라 조회 가능한 수강 신청 목록을 반환합니다.

        Returns:
            QuerySet: 필터링된 Enrollment 목록.
        """
        if self.request.user.is_staff or self.request.user.role == "manager":
            return Enrollment.objects.all()
        return Enrollment.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        새로운 수강 신청을 생성합니다.

        Args:
            request (HttpRequest): 요청 객체.

        Returns:
            Response: 생성된 수강 신청 정보 또는 오류 메시지.
        """
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
        """
        수강 신청 생성 작업을 수행합니다.

        Args:
            serializer (Serializer): 수강 신청 데이터 시리얼라이저.
        """
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
        """
        활성 상태의 수강 신청 목록을 반환합니다.

        Args:
            request (HttpRequest): 요청 객체.

        Returns:
            Response: 활성 상태의 수강 신청 목록.
        """
        active_enrollments = self.get_queryset().filter(status="active")
        serializer = self.get_serializer(active_enrollments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def complete_enrollment(self, request, pk=None):
        """
        수강 신청을 완료 상태로 변경합니다.

        Args:
            request (HttpRequest): 요청 객체.
            pk (int): 수강 신청의 기본 키.

        Returns:
            Response: 수강 신청 완료 메시지 또는 오류 메시지.
        """
        enrollment = self.get_object()
        if enrollment.status == "active":
            enrollment.status = "completed"
            enrollment.save()
            return Response({"status": "enrollment completed"})
        return Response(
            {"status": "enrollment cannot be completed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

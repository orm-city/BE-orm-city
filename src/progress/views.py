from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import UserProgress
from courses.models import Enrollment, MajorCategory
from videos.models import Video
from .serializers import (
    UserProgressSerializer,
    UserProgressUpdateSerializer,
    OverallProgressSerializer,
    VideoProgressSerializer,
)
from .services import UserProgressService
from .permissions import CanViewUserProgress
import logging


logger = logging.getLogger(__name__)


class UserProgressListView(generics.ListAPIView):  # 테스트 완료
    """
    현재 로그인한 사용자의 모든 비디오에 대한 학습 진행 상황을 제공하는 뷰

    이 뷰는 GET 요청에 대해 현재 인증된 사용자의 모든 비디오별 학습 진행 정보를 반환합니다.
    """

    permission_classes = [CanViewUserProgress]
    serializer_class = UserProgressSerializer

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)


class UserProgressUpdateView(generics.UpdateAPIView):  # 테스트 완료
    """
    사용자의 특정 비디오에 대한 학습 진행 상황을 업데이트하는 뷰

    이 뷰는 PATCH 요청을 통해 특정 비디오에 대한 사용자의 학습 진행 상황을 업데이트합니다.
    Enrollment 검사를 통해 유효한 수강 신청 상태인지 확인합니다.
    """

    permission_classes = [CanViewUserProgress]
    serializer_class = UserProgressUpdateSerializer
    queryset = UserProgress.objects.all()

    def update(self, request, *args, **kwargs):
        logger.debug(f"received data: {request.data}")
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        additional_time = serializer.validated_data["additional_time"]
        last_position = serializer.validated_data["last_position"]

        try:
            # Enrollment 검사
            enrollment = get_object_or_404(
                Enrollment,
                user=request.user,
                major_category=instance.video.minor_category.major_category,
            )

            if enrollment.status != "active":
                return Response(
                    {"error": "Enrollment is not active"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            updated_instance = UserProgressService.update_progress(
                instance,
                instance.progress_percent,  # 현재 진행률 유지
                additional_time,
                last_position,
            )

            return Response(UserProgressSerializer(updated_instance).data)
        except Enrollment.DoesNotExist:
            return Response(
                {"error": "No valid enrollment found for this user and video"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to update progress: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserOverallProgressView(APIView):
    permission_classes = [CanViewUserProgress]
    """
    사용자의 전체 학습 진행 상황을 제공하는 뷰

    이 뷰는 GET 요청에 대해 현재 인증된 사용자의 전체 학습 진행률과
    각 대분류(MajorCategory)별 진행률을 반환합니다.
    """

    def get(self, request):
        user = request.user
        major_categories = MajorCategory.objects.all()

        overall_progress = (
            UserProgress.objects.filter(user=user).aggregate(Avg("progress_percent"))[
                "progress_percent__avg"
            ]
            or 0
        )

        category_progress = []
        for category in major_categories:
            videos = Video.objects.filter(minor_category__major_category=category)
            progress = (
                UserProgress.objects.filter(user=user, video__in=videos).aggregate(
                    Avg("progress_percent")
                )["progress_percent__avg"]
                or 0
            )
            category_progress.append(
                {"category_name": category.name, "progress_percent": progress}
            )

        serializer = OverallProgressSerializer(
            {
                "overall_progress": overall_progress,
                "category_progress": category_progress,
            }
        )
        return Response(serializer.data)


# 테스트완료
class UserProgressDetailView(generics.RetrieveAPIView):
    """
    사용자의 특정 비디오에 대한 학습 진행 상황을 제공하는 뷰

    이 뷰는 GET 요청에 대해 현재 인증된 사용자의 특정 비디오에 대한 학습 진행 정보를 반환합니다.
    """

    permission_classes = [CanViewUserProgress]
    serializer_class = VideoProgressSerializer

    def get_object(self):
        video_id = self.kwargs.get("video_id")
        video = get_object_or_404(Video, id=video_id)

        enrollment = get_object_or_404(
            Enrollment,
            user=self.request.user,
            major_category=video.minor_category.major_category,
        )

        user_progress, created = UserProgress.objects.get_or_create(
            user=self.request.user, video=video, enrollment=enrollment
        )

        return user_progress

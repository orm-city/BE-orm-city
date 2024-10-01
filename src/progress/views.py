from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import UserProgress
from .serializers import (
    UserProgressSerializer,
    UserProgressUpdateSerializer,
    UserOverallProgressSerializer,
)
from videos.models import Video


class UserOverallProgressView(APIView):
    """
    사용자의 전체 학습 진행 상황 요약을 제공하는 뷰.
    """

    def get(self, request):
        user = request.user
        progresses = UserProgress.objects.filter(user=user)

        total_videos = progresses.count()
        completed_videos = progresses.filter(is_completed=True).count()

        # 전체 진행률 계산 (완료된 비디오 / 전체 비디오)
        overall_progress = (
            (completed_videos / total_videos) * 100 if total_videos > 0 else 0
        )

        data = {
            "total_videos": total_videos,
            "completed_videos": completed_videos,
            "overall_progress_percent": round(overall_progress, 2),
            "total_time_spent": sum(
                (p.time_spent for p in progresses), timezone.timedelta()
            ),
        }
        serializer = UserOverallProgressSerializer(data)
        return Response(serializer.data)


class UserProgressDetailView(generics.RetrieveAPIView):
    """
    특정 비디오에 대한 사용자의 학습 진행 상황을 조회하는 뷰.
    """

    serializer_class = UserProgressSerializer

    def get_object(self):
        video_id = self.kwargs["video_id"]
        # 주의: 해당 비디오에 대한 진행 정보가 없을 경우 404 에러 발생
        return UserProgress.objects.get(user=self.request.user, video_id=video_id)


class UpdateUserProgressView(generics.UpdateAPIView):
    """
    특정 비디오에 대한 사용자의 학습 진행 상황을 업데이트하는 뷰.
    """

    serializer_class = UserProgressUpdateSerializer

    def update(self, request, *args, **kwargs):
        video_id = self.kwargs["video_id"]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            video = Video.objects.get(id=video_id)
            # 진행 정보가 없으면 생성, 있으면 가져오기
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                video=video,
                defaults={
                    "enrollment": video.minor_category.enrollments.get(
                        user=request.user
                    )
                },
            )

            # 진행 상황 업데이트
            progress.update_progress(
                serializer.validated_data["progress_percent"],
                timezone.timedelta(
                    seconds=serializer.validated_data["additional_time"]
                ),
                serializer.validated_data["last_position"],
            )

            return Response(UserProgressSerializer(progress).data)
        except Video.DoesNotExist:
            return Response(
                {"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # 기타 예외 처리 (예: 사용자가 해당 강의에 등록되지 않은 경우 등)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

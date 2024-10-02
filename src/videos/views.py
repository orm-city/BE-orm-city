from urllib.parse import urlparse
from uuid import uuid4

from django.conf import settings
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from botocore.exceptions import ClientError

from courses.models import Enrollment, MinorCategory
from progress.models import UserProgress
from progress.services import UserProgressService
from .permissions import IsAdminUser, IsEnrolledOrAdmin
from .models import Video
from .serializers import ProgressUpdateSerializer, VideoSerializer
from .services import (
    get_s3_client,
    get_presigned_post,
    get_presigned_url,
)


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.action in ["update", "destroy", "create"]:
            return [IsAdminUser()]
        elif self.action in ["retrieve", "list"]:
            return [IsEnrolledOrAdmin()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        try:
            presigned_post = get_presigned_post()
            s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{presigned_post['fields']['key']}"

            video = Video.objects.create(
                name=request.data.get("name", "Auto-generated name"),
                description=request.data.get(
                    "description", "Auto-generated description"
                ),
                duration=request.data.get("duration", timezone.timedelta(seconds=0)),
                video_url=s3_url,
                minor_category=MinorCategory.objects.first(),
            )

            return Response(
                {"presigned_post": presigned_post, "video_id": video.id},
                status=status.HTTP_201_CREATED,
            )
        except ClientError as e:
            return Response(
                {"detail": f"S3 URL 생성 중 오류 발생: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        video = self.get_object()
        try:
            presigned_url = get_presigned_url(video.video_url)
            user = request.user

            user_progress = UserProgress.objects.filter(user=user, video=video).first()
            last_position = user_progress.last_position if user_progress else 0

            return Response(
                {"video_url": presigned_url, "last_position": last_position},
                status=status.HTTP_200_OK,
            )
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ClientError as e:
            return Response(
                {"detail": f"Failed to generate presigned URL: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        video = self.get_object()
        s3_client = get_s3_client()

        # 기존 S3 객체 삭제
        try:
            parsed_url = urlparse(video.video_url)
            bucket_name = parsed_url.netloc.split(".")[0]
            object_key = parsed_url.path.lstrip("/")
            s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        except ClientError as e:
            return Response(
                {"detail": f"기존 비디오 삭제 중 오류 발생: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"detail": f"비디오 삭제 중 알 수 없는 오류 발생: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 새 Presigned URL 생성
        try:
            filename = str(uuid4()) + ".mp4"
            presigned_post = s3_client.generate_presigned_post(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=filename,
                Fields={"Content-Type": "video/mp4"},
                Conditions=[
                    {"Content-Type": "video/mp4"},
                    ["content-length-range", 1, 1024 * 1024 * 500],
                ],
                ExpiresIn=120,
            )

            video.video_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"
            video.save()

            UserProgress.objects.filter(video=video).update(last_position=0)

            return Response(
                {"presigned_post": presigned_post, "video_id": video.id},
                status=status.HTTP_200_OK,
            )
        except ClientError as e:
            return Response(
                {"detail": f"S3 URL 생성 중 오류 발생: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"detail": f"S3 Presigned URL 생성 중 알 수 없는 오류 발생: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        video = self.get_object()
        s3_client = get_s3_client()

        # S3에서 파일 삭제

        try:
            parsed_url = urlparse(video.video_url)
            object_key = parsed_url.path.lstrip("/")
            s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=object_key
            )
        except ClientError as e:
            return Response(
                {"detail": f"S3 파일 삭제 중 오류 발생: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"detail": f"파일 삭제 중 알 수 없는 오류 발생: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        video.delete()
        return Response(
            {"detail": "Video deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class UpdateUserProgressAPIView(APIView):
    permission_classes = [IsEnrolledOrAdmin]
    throttle_scope = "progress"

    def post(self, request, *args, **kwargs):
        # 데이터 검증
        serializer = ProgressUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 검증된 데이터 가져오기
        video_id = serializer.validated_data["video_id"]
        progress_percent = serializer.validated_data["progress_percent"]
        time_spent = serializer.validated_data["time_spent"]
        last_position = serializer.validated_data["last_position"]

        user = request.user

        try:
            progress_percent = int(progress_percent)
            last_position = int(last_position)
            if not (0 <= progress_percent <= 100):
                raise ValueError("progress_percent는 0과 100 사이여야 합니다.")
            if last_position < 0:
                raise ValueError("last_position는 0 이상이어야 합니다.")
            time_spent = int(time_spent)
            if time_spent < 0:
                raise ValueError("time_spent는 양수여야 합니다.")
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
            major_category = video.minor_category.major_category
            enrollment = Enrollment.objects.get(
                user=user, major_category=major_category
            )

            user_progress, created = UserProgress.objects.get_or_create(
                user=user, video=video, enrollment=enrollment
            )
            if created:
                UserProgressService.reset_progress(user_progress)

            UserProgressService.update_progress(
                progress_percent, timezone.timedelta(seconds=time_spent), last_position
            )

            return Response(
                {"detail": "Progress updated successfully"}, status=status.HTTP_200_OK
            )
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Enrollment.DoesNotExist:
            return Response(
                {"detail": "Enrollment not found for this user and course."},
                status=status.HTTP_404_NOT_FOUND,
            )

from uuid import uuid4
import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from progress.models import UserProgress
from .models import Video
from .serializers import VideoSerializer


class VideoUploadPermissionAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # 현재 요청을 보낸 사용자의 role이 admin인지 확인
        # user = request.user
        # if user.role != "admin":
        #     return Response(
        #         {"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
        #     )

        try:
            presigned_post = self.get_presigned_post()

            # 데이터베이스에 presigned_url 저장
            video = Video.objects.create(
                # name=f"Video by {user.username}",
                name="Video by username",
                description="Auto-generated description",
                video_url=presigned_post["url"],  # presigned URL 저장
                created_at=None,  # 자동 생성되므로 생략 가능
            )

            return Response(
                {
                    "presigned_post": presigned_post,
                    "video_id": video.id,  # 나중에 사용하기 위해 반환 가능
                },
                status=status.HTTP_200_OK,
            )
        except ClientError as e:
            return Response(
                {"detail": "S3 URL 생성 중 오류 발생: {}".format(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_presigned_post(self):
        """
        2분 동안 유효한 AWS S3 버킷의 사전 서명된 URL을 생성합니다.
        :return: 사전 서명된 POST URL
        """
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        # 유니크한 파일명 생성
        filename = str(uuid4()) + ".mp4"

        try:
            presigned_post = s3_client.generate_presigned_post(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=filename,
                Fields={"Content-Type": "video/mp4"},
                Conditions=[
                    {"Content-Type": "video/mp4"},
                    ["content-length-range", 1, 1024 * 1024 * 500],  # 최대 500MB
                ],
                ExpiresIn=120,  # 2분 동안 유효
            )

            return presigned_post
        except ClientError as e:
            raise e


class VideoRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [AllowAny]


class VideoUpdateAPIView(generics.UpdateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [AllowAny]

    def put(self, request, *args, **kwargs):
        video = self.get_object()

        try:
            # 새로운 presigned URL 생성
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

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

            # 기존 Video 객체 업데이트
            video.video_url = presigned_post["url"]
            video.save()

            return Response(
                {"presigned_post": presigned_post, "video_id": video.id},
                status=status.HTTP_200_OK,
            )

        except ClientError as e:
            return Response(
                {"detail": "S3 URL 생성 중 오류 발생: {}".format(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VideoDeleteAPIView(generics.DestroyAPIView):
    queryset = Video.objects.all()
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        video = self.get_object()
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        # S3에서 파일 삭제
        key = video.video_url.split("/")[-1]  # video_url에서 S3 키 추출
        try:
            s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        except ClientError as e:
            return Response(
                {"detail": "S3 파일 삭제 중 오류 발생: {}".format(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 데이터베이스에서 Video 객체 삭제
        video.delete()
        return Response(
            {"detail": "Video deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class UpdateUserProgressAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        video_id = request.data.get("video_id")
        progress_percent = request.data.get("progress_percent")
        time_spent = request.data.get("time_spent")

        try:
            video = Video.objects.get(id=video_id)
            user_progress, created = UserProgress.objects.get_or_create(
                user=user, video=video
            )
            user_progress.update_progress(
                progress_percent, timezone.timedelta(seconds=time_spent)
            )

            return Response(
                {"detail": "Progress updated successfully"}, status=status.HTTP_200_OK
            )
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video not found"}, status=status.HTTP_404_NOT_FOUND
            )

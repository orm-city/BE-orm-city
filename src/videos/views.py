from uuid import uuid4
import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from urllib.parse import urlparse

from progress.models import UserProgress
from .models import Video
from .serializers import VideoSerializer

from django.contrib.auth import get_user_model  # 테스트용 코드
from courses.models import Enrollment, MinorCategory  # 테스트용 코드


class VideoUploadPermissionAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            presigned_post = self.get_presigned_post()

            # S3 URL 생성 (객체 키를 포함한 전체 경로)
            s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{presigned_post['fields']['key']}"

            # 데이터베이스에 s3_url 저장
            video = Video.objects.create(
                name="Video by username",
                description="Auto-generated description",
                video_url=s3_url,  # 전체 S3 URL을 저장
                minor_category=MinorCategory.objects.first(),  # 임의의 MinorCategory
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


class VideoRetrieveAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        video_id = kwargs.get("pk")
        try:
            video = Video.objects.get(id=video_id)
            presigned_url = self.get_presigned_url(video.video_url)
            # user = request.user
            User = get_user_model()
            user = User.objects.get(id=2)

            # 해당 비디오에 대한 유저의 진행 정보 가져오기
            # user_progress = UserProgress.objects.filter(user=user, video=video).first()
            user_progress = UserProgress.objects.filter(user=user, video=video).first()
            last_position = user_progress.last_position if user_progress else 0

            return Response(
                {
                    "video_url": presigned_url,
                    "last_position": last_position,
                },
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

    def get_presigned_url(self, s3_url):
        """
        S3 객체에 대한 사전 서명된 URL을 생성합니다.
        :param s3_url: S3에 저장된 객체의 URL
        :return: 사전 서명된 GET URL
        """
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        # s3_url에서 객체 키를 올바르게 추출
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        parsed_url = urlparse(s3_url)
        object_key = parsed_url.path.lstrip("/")

        try:
            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_key},
                ExpiresIn=3600,  # 1시간 동안 유효
            )
            return presigned_url
        except ClientError as e:
            raise e


class VideoUpdateAPIView(generics.UpdateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [AllowAny]

    def put(self, request, *args, **kwargs):
        video = self.get_object()

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        # 기존 S3 객체 삭제
        try:
            parsed_url = urlparse(video.video_url)
            bucket_name = parsed_url.netloc.split(".")[0]
            object_key = parsed_url.path.lstrip("/")

            s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        except ClientError as e:
            return Response(
                {"detail": "기존 비디오 삭제 중 오류 발생: {}".format(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 새로운 presigned URL 생성 및 S3에 업로드
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

            # 새 URL로 video_url 필드 업데이트
            video.video_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"
            video.save()

            UserProgress.objects.filter(video=video).update(
                progress_percent=0,
                time_spent=timezone.timedelta(0),
                last_position=0,
                is_completed=False,
            )

            return Response(
                {"presigned_post": presigned_post, "video_id": video.id},
                status=status.HTTP_200_OK,
            )

        except ClientError as e:
            return Response(
                {"detail": "새로운 S3 URL 생성 중 오류 발생: {}".format(e)},
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
        parsed_url = urlparse(video.video_url)
        key = parsed_url.path.lstrip("/")  # S3 객체 키 추출
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
    permission_classes = [AllowAny]  # TODO: 실제 배포 시 IsAuthenticated로 변경

    def post(self, request, *args, **kwargs):
        User = get_user_model()
        user = User.objects.get(id=2)  # 실제 환경에서는 request.user를 사용하세요.

        video_id = request.data.get("video_id")
        progress_percent = request.data.get("progress_percent")
        time_spent = request.data.get("time_spent")
        last_position = request.data.get("last_position")  # 추가된 필드

        if (
            not video_id
            or progress_percent is None
            or time_spent is None
            or last_position is None
        ):
            return Response(
                {"detail": "요청 데이터가 누락되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
            minor_category = video.minor_category
            enrollment = Enrollment.objects.get(
                user=user, minor_category=minor_category
            )

            user_progress, created = UserProgress.objects.get_or_create(
                user=user, video=video, enrollment=enrollment
            )
            user_progress.update_progress(
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

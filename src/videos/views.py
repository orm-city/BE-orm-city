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
    """
    클라이언트가 비디오 파일을 AWS S3 버킷에 업로드하기 위한 사전 서명된 URL을 요청할 수 있는 API 뷰입니다.
    이 뷰는 비디오 업로드를 위한 presign_url을 생성하고, 해당 URL을 데이터베이스에 저장된 비디오 객체와 함께 반환합니다.

    Methods:
        get(request, *args, **kwargs):
            클라이언트로부터 GET 요청을 처리하여 사전 서명된 S3 URL을 생성하고, 비디오 객체를 데이터베이스에 저장한 후 URL과 비디오 ID를 반환합니다.

        get_presigned_post():
            AWS S3에 비디오 파일을 업로드하기 위한 사전 서명된 POST URL을 생성합니다.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        클라이언트로부터 GET 요청을 처리하여 AWS S3 버킷에 비디오 파일을 업로드하기 위한
        사전 서명된 URL을 생성하고, 해당 URL과 비디오 객체의 ID를 반환합니다.

        Returns:
            Response: presigned URL과 비디오 객체의 ID가 포함된 JSON 응답.
            HTTP 200: URL과 비디오 ID가 성공적으로 생성된 경우.
            HTTP 500: S3 URL 생성 중 오류가 발생한 경우.
        """
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
        AWS S3 버킷에 비디오 파일을 업로드하기 위한 사전 서명된 POST URL을 생성합니다.

        Returns:
            dict: 사전 서명된 POST URL과 관련된 필드들을 포함한 딕셔너리.

        Raises:
            ClientError: S3 URL 생성 중 오류가 발생할 경우 예외를 발생시킵니다.
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
    """
    특정 비디오의 정보를 조회하고, 해당 비디오 파일에 대한 S3 presign_url을 생성하여 반환하는 API 뷰입니다.

    Methods:
        get(request, *args, **kwargs):
            클라이언트로부터 GET 요청을 처리하여 비디오 객체를 조회하고, S3 사전 서명된 URL과 사용자의 마지막 시청 위치를 반환합니다.

        get_presigned_url(s3_url):
            S3에 저장된 객체에 대한 사전 서명된 GET URL을 생성합니다.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        비디오 ID를 기반으로 비디오 객체를 조회하고, 해당 비디오 파일에 대한 S3 사전 서명된 URL과
        사용자의 마지막 시청 위치를 반환합니다.

        Args:
            request (HttpRequest): 클라이언트로부터 전달된 HTTP 요청 객체.
            *args: 가변 인자 리스트.
            **kwargs: URL 패턴에서 전달된 추가적인 키워드 인자들, 여기서는 비디오 ID (pk)를 포함합니다.

        Returns:
            Response: 비디오 URL과 사용자의 마지막 시청 위치가 포함된 JSON 응답.
            HTTP 200: 요청이 성공적으로 처리된 경우.
            HTTP 404: 비디오 객체를 찾을 수 없는 경우.
            HTTP 500: S3 URL 생성 중 오류가 발생한 경우.
        """
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
        S3 객체에 접근할 수 있는 사전 서명된 GET URL을 생성합니다.

        Args:
            s3_url (str): S3에 저장된 객체의 URL.

        Returns:
            str: S3 객체에 접근할 수 있는 사전 서명된 GET URL.

        Raises:
            ClientError: S3 URL 생성 중 오류가 발생할 경우 예외를 발생시킵니다.
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
    """

    이 뷰는 기존 S3에 저장된 비디오 파일을 삭제하고, 새로운 비디오 파일을 업로드하기 위한 사전 서명된 URL을 생성한 후,
    비디오 객체의 URL을 새로 생성된 S3 URL로 업데이트합니다.

    Attributes:
        queryset (QuerySet): 업데이트할 비디오 객체의 쿼리셋입니다. 모든 비디오 객체를 대상으로 합니다.
        serializer_class (Serializer): 비디오 객체를 직렬화하는 데 사용되는 직렬화 클래스입니다.
        permission_classes (list): 이 API 뷰에 접근할 수 있는 권한을 정의합니다. `AllowAny`로 설정되어 있어, 인증되지 않은 사용자도 이 엔드포인트에 접근할 수 있습니다.

    Methods:
        put(request, *args, **kwargs):
            클라이언트로부터 PUT 요청을 처리하여 기존 비디오 객체를 S3에서 삭제하고, 새로운 S3 URL로 비디오 객체를 업데이트합니다.
    """

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [AllowAny]

    def put(self, request, *args, **kwargs):
        """
        기존 비디오 객체를 업데이트하고, 새로운 비디오 파일을 업로드하기 위한 S3 사전 서명된 URL을 생성하여 반환합니다.

        기존 S3 객체를 삭제한 후, 새로운 객체를 업로드할 수 있는 URL을 생성하고,
        비디오 객체의 URL을 새로 생성된 URL로 업데이트합니다. 또한, 비디오에 대한 진행 정보를 초기화합니다.

        Returns:
            Response: 새로 생성된 S3 URL과 업데이트된 비디오 객체의 ID가 포함된 JSON 응답.
            HTTP 200: 요청이 성공적으로 처리된 경우.
            HTTP 500: S3 객체 삭제 또는 생성 중 오류가 발생한 경우.
        """
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
    """
    클라이언트가 특정 비디오 객체를 삭제할 수 있는 API 뷰입니다.

    이 뷰는 S3에서 해당 비디오 파일을 삭제하고, 데이터베이스에서 해당 비디오 객체를 제거합니다.

    Attributes:
        queryset (QuerySet): 삭제할 비디오 객체의 쿼리셋입니다. 모든 비디오 객체를 대상으로 합니다.
        permission_classes (list): 이 API 뷰에 접근할 수 있는 권한을 정의합니다. `AllowAny`로 설정되어 있어, 인증되지 않은 사용자도 이 엔드포인트에 접근할 수 있습니다.

    Methods:
        delete(request, *args, **kwargs):
            클라이언트로부터 DELETE 요청을 처리하여 S3에서 비디오 파일을 삭제하고, 데이터베이스에서 비디오 객체를 제거합니다.
    """

    queryset = Video.objects.all()
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        """
        특정 비디오 객체를 삭제하고, S3에서 해당 비디오 파일을 제거합니다.

        Args:
            request (HttpRequest): 클라이언트로부터 전달된 HTTP 요청 객체.
            *args: 가변 인자 리스트.
            **kwargs: URL 패턴에서 전달된 추가적인 키워드 인자들.

        Returns:
            Response: 비디오 객체가 성공적으로 삭제되었음을 알리는 JSON 응답.
            HTTP 204: 비디오 객체가 성공적으로 삭제된 경우.
            HTTP 500: S3에서 파일을 삭제하는 중 오류가 발생한 경우.
        """
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
    """
    사용자의 비디오 시청 진행 정보를 업데이트할 수 있는 API 뷰입니다.

    이 뷰는 사용자가 특정 비디오에 대해 시청한 진행 상태를 업데이트합니다.
    요청 데이터에는 비디오 ID, 진행 비율, 시청 시간, 마지막 재생 위치가 포함되어야 합니다.

    Methods:
        post(request, *args, **kwargs):
            클라이언트로부터 POST 요청을 받아 사용자의 비디오 시청 진행 정보를 업데이트합니다.
    """

    permission_classes = [AllowAny]  # TODO: 실제 배포 시 IsAuthenticated로 변경

    def post(self, request, *args, **kwargs):
        """
        사용자의 비디오 시청 진행 정보를 업데이트합니다.

        요청 데이터로 비디오 ID, 진행 비율, 시청 시간, 마지막 재생 위치를 받아, 해당 비디오에 대한 사용자의 진행 정보를 업데이트합니다.

        Args:
            request (HttpRequest): 클라이언트로부터 전달된 HTTP 요청 객체.
            *args: 가변 인자 리스트.
            **kwargs: URL 패턴에서 전달된 추가적인 키워드 인자들.

        Returns:
            Response: 진행 정보가 성공적으로 업데이트되었음을 알리는 JSON 응답.
            HTTP 200: 진행 정보가 성공적으로 업데이트된 경우.
            HTTP 400: 요청 데이터가 잘못되었거나 누락된 경우.
            HTTP 404: 비디오 또는 등록 정보를 찾을 수 없는 경우.
        """
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

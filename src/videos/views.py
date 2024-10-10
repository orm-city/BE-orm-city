from datetime import timedelta
from urllib.parse import urlparse

from django.conf import settings
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from botocore.exceptions import ClientError
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
)

from courses.models import Enrollment, MinorCategory
from progress.models import UserProgress
from progress.services import UserProgressService
from .permissions import IsManagerOrAdmin, IsEnrolledOrAdminOrManager
from .models import Video
from .serializers import VideoSerializer
from .services import (
    check_multipart_upload_status,
    get_s3_client,
    initiate_multipart_upload,
    generate_presigned_urls_for_parts,
    complete_multipart_upload,
    get_presigned_url,
)


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of videos",
        responses={200: VideoSerializer(many=True)},
        tags=["videos"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single video with presigned URL and user progress",
        responses={
            200: OpenApiResponse(
                description="Returns the video presigned URL and user's last position",
                examples=[
                    {
                        "video_url": "https://s3.amazonaws.com/example/video.mp4",
                        "last_position": 120,
                    }
                ],
            ),
            404: OpenApiResponse(description="Video not found"),
            500: OpenApiResponse(description="Failed to generate presigned URL"),
        },
        tags=["videos"],
    ),
    create=extend_schema(
        summary="Create a new video and initiate multipart upload",
        parameters=[
            OpenApiParameter(
                name="total_parts",
                description="Total parts for multipart upload",
                required=True,
                type=int,
            ),
            OpenApiParameter(
                name="duration",
                description="Duration of the video in seconds",
                required=True,
                type=int,
            ),
            OpenApiParameter(
                name="minor_category_id",
                description="ID of the minor category",
                required=True,
                type=int,
            ),
        ],
        responses={
            201: OpenApiResponse(
                description="Upload initiated and presigned URLs returned",
                examples=[
                    {
                        "upload_id": "exampleUploadId",
                        "presigned_urls": ["https://s3.amazonaws.com/..."],
                        "video_id": 1,
                        "filename": "video.mp4",
                    }
                ],
            ),
            500: OpenApiResponse(description="Error during S3 URL generation"),
        },
        tags=["videos"],
    ),
    update=extend_schema(
        summary="Update a video and reset progress",
        parameters=[
            OpenApiParameter(
                name="total_parts",
                description="Total parts for multipart upload",
                required=True,
                type=int,
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Video updated and presigned URLs returned",
                examples=[
                    {
                        "upload_id": "exampleUploadId",
                        "presigned_urls": ["https://s3.amazonaws.com/..."],
                        "video_id": 1,
                        "filename": "new_video.mp4",
                    }
                ],
            ),
            500: OpenApiResponse(
                description="Error during S3 URL generation or deletion"
            ),
        },
        tags=["videos"],
    ),
    destroy=extend_schema(
        summary="Delete a video and remove from S3",
        responses={
            204: OpenApiResponse(description="Video deleted successfully"),
            500: OpenApiResponse(description="Error during S3 deletion"),
        },
        tags=["videos"],
    ),
)
class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        if self.action in ["update", "destroy", "create"]:
            return [IsManagerOrAdmin()]
        elif self.action in ["retrieve"]:
            return [IsEnrolledOrAdminOrManager()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        try:
            upload_id, filename = initiate_multipart_upload()
            print(f"Initiated upload with ID: {upload_id}")

            total_parts = int(request.data.get("total_parts"))

            # 3. 각 파트에 대해 presigned URL 생성
            presigned_urls = generate_presigned_urls_for_parts(
                upload_id, filename, total_parts
            )

            # 프론트엔드에서 받은 duration 값 (초 단위)
            duration_in_seconds = request.data.get("duration", 0)
            duration_timedelta = timedelta(seconds=duration_in_seconds)

            # minor_category_id로 minor_category 찾기
            minor_category_id = request.data.get("minor_category_id")
            minor_category = MinorCategory.objects.get(id=minor_category_id)

            # Video 객체 생성
            video = Video.objects.create(
                name=request.data.get("name", "Auto-generated name"),
                description=request.data.get(
                    "description", "Auto-generated description"
                ),
                duration=duration_timedelta,
                video_url=f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}",
                minor_category=minor_category,
            )

            return Response(
                {
                    "upload_id": upload_id,
                    "presigned_urls": presigned_urls,
                    "video_id": video.id,
                    "filename": filename,
                },
                status=status.HTTP_201_CREATED,
            )

        except ClientError as e:
            # S3 오류 처리
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

        # 새 비디오에 대한 멀티파트 업로드 생성
        try:
            # 1. 멀티파트 업로드 시작
            upload_id, filename = initiate_multipart_upload()

            # 2. 클라이언트가 요청한 총 파트 수를 가져옴
            total_parts = int(request.data.get("total_parts"))

            # 3. 각 파트에 대해 presigned URL 생성
            presigned_urls = generate_presigned_urls_for_parts(
                upload_id, filename, total_parts
            )

            # 비디오 URL 업데이트
            video.video_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"
            video.save()

            # 비디오 프로그레스 초기화
            UserProgress.objects.filter(video=video).update(last_position=0)

            # 4. 클라이언트에게 presigned URL 및 업로드 ID 반환
            return Response(
                {
                    "upload_id": upload_id,
                    "presigned_urls": presigned_urls,
                    "video_id": video.id,
                    "filename": filename,
                },
                status=status.HTTP_200_OK,
            )

        except ClientError as e:
            return Response(
                {"detail": f"새 비디오 업로드 중 오류 발생: {e}"},
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


@extend_schema(
    summary="Complete multipart upload",
    description="This endpoint completes a multipart upload by verifying the parts and finalizing the upload in S3.",
    request={
        "application/json": {
            "upload_id": "string",
            "filename": "string",
            "parts": [
                {"PartNumber": 1, "ETag": "string"},
                {"PartNumber": 2, "ETag": "string"},
            ],
        }
    },
    responses={
        200: OpenApiResponse(
            description="Upload completed successfully",
            examples={
                "application/json": {
                    "detail": "Upload completed successfully",
                    "response": {"ETag": "example-etag"},
                }
            },
        ),
        400: OpenApiResponse(
            description="Bad request due to missing or invalid fields",
            examples={
                "application/json": {
                    "detail": "upload_id, filename, 그리고 parts 필드가 필요합니다."
                }
            },
        ),
        500: OpenApiResponse(
            description="Server error during upload completion",
            examples={
                "application/json": {
                    "detail": "Upload completion failed: error message"
                }
            },
        ),
    },
    tags=["videos"],
)
class CompleteUploadAPIView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def post(self, request, *args, **kwargs):
        upload_id = request.data.get("upload_id")
        filename = request.data.get("filename")
        parts = request.data.get("parts")

        print(f"Received completion request for upload ID: {upload_id}")

        if not upload_id or not filename or not parts:
            return Response(
                {"detail": "upload_id, filename, 그리고 parts 필드가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 업로드 상태 확인
            uploaded_parts = check_multipart_upload_status(upload_id, filename)

            if uploaded_parts is None:
                return Response(
                    {
                        "detail": "Upload not found or expired. Please start a new upload."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 클라이언트가 보낸 parts와 실제 업로드된 parts 비교
            if len(uploaded_parts) != len(parts):
                return Response(
                    {"detail": "업로드된 파트 수가 일치하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ETag 비교 (선택적)
            for client_part, uploaded_part in zip(parts, uploaded_parts):
                if client_part["ETag"].strip('"') != uploaded_part["ETag"].strip('"'):
                    return Response(
                        {
                            "detail": f"파트 {client_part['PartNumber']}의 ETag가 일치하지 않습니다."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # 멀티파트 업로드 완료 처리
            response = complete_multipart_upload(upload_id, filename, parts)
            return Response(
                {"detail": "Upload completed successfully", "response": response},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(f"Error during upload completion: {str(e)}")
            return Response(
                {"detail": f"Upload completion failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


throttle_scope = ("progress",)


@extend_schema(
    summary="Update User Video Progress",
    description="This endpoint updates the user's progress for a specific video, including progress percentage, time spent, and last watched position.",
    request={
        "application/json": {
            "video_id": "integer",
            "progress_percent": "integer (0-100)",
            "time_spent": "integer (seconds)",
            "last_position": "integer (in seconds)",
        }
    },
    responses={
        200: OpenApiResponse(
            description="Progress updated successfully",
            examples={"application/json": {"detail": "Progress updated successfully"}},
        ),
        400: OpenApiResponse(
            description="Bad request due to missing or invalid fields",
            examples={"application/json": {"detail": "요청 데이터가 누락되었습니다."}},
        ),
        404: OpenApiResponse(
            description="Video or Enrollment not found",
            examples={
                "application/json": {"detail": "Video not found"},
            },
        ),
        429: OpenApiResponse(
            description="Request was throttled due to too many requests in a short time",
            examples={
                "application/json": {
                    "detail": "Request was throttled. Try again later."
                }
            },
        ),
        500: OpenApiResponse(
            description="Internal server error",
            examples={
                "application/json": {
                    "detail": "An error occurred while processing the request."
                }
            },
        ),
    },
    tags=["videos"],
)
class UpdateUserProgressAPIView(APIView):
    permission_classes = [IsEnrolledOrAdminOrManager]
    throttle_scope = "progress"

    def post(self, request, *args, **kwargs):
        user = request.user

        video_id = request.data.get("video_id")
        progress_percent = request.data.get("progress_percent")
        time_spent = request.data.get("time_spent")
        last_position = request.data.get("last_position")

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
                user_progress,
                progress_percent,
                timezone.timedelta(seconds=time_spent),
                last_position,
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

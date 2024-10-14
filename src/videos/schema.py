from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

video_list_schema = extend_schema(
    summary="Retrieve a list of videos",
    responses={200: "VideoSerializer(many=True)"},
    tags=["videos"],
)

video_retrieve_schema = extend_schema(
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
)

video_create_schema = extend_schema(
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
)

video_update_schema = extend_schema(
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
)

video_destroy_schema = extend_schema(
    summary="Delete a video and remove from S3",
    responses={
        204: OpenApiResponse(description="Video deleted successfully"),
        500: OpenApiResponse(description="Error during S3 deletion"),
    },
    tags=["videos"],
)


# CompleteUploadAPIView 스키마
complete_upload_schema = extend_schema(
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

# UpdateUserProgressAPIView 스키마
update_user_progress_schema = extend_schema(
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


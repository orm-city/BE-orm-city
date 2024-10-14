from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    UserProgressSerializer,
    UserProgressUpdateSerializer,
    OverallProgressSerializer,
    VideoProgressSerializer,
)

# UserProgressListView 스키마 정의
user_progress_list_schema = extend_schema(
    summary="사용자의 모든 학습 진행 상황 조회",
    description="현재 로그인한 사용자의 비디오별 학습 진행 상황을 조회하는 API입니다.",
    responses={
        200: OpenApiResponse(
            description="성공적으로 사용자의 학습 진행 데이터를 반환합니다.",
            response=UserProgressSerializer(many=True),
        ),
        401: OpenApiResponse(description="인증되지 않은 사용자입니다."),
    },
)

# UserProgressUpdateView 스키마 정의
user_progress_update_schema = extend_schema(
    summary="사용자의 학습 진행 상황 업데이트",
    description="현재 로그인한 사용자의 특정 비디오 학습 진행 상황을 업데이트하는 API입니다. 유효한 수강 신청 상태인지를 확인한 후 학습 데이터를 갱신합니다.",
    request=UserProgressUpdateSerializer,
    responses={
        200: OpenApiResponse(
            description="성공적으로 업데이트된 학습 진행 정보를 반환합니다.",
            response=UserProgressSerializer,
        ),
        400: OpenApiResponse(description="유효하지 않은 요청 또는 학습 진행 상황 업데이트 실패"),
        401: OpenApiResponse(description="인증되지 않은 사용자입니다."),
    },
)


# UserOverallProgressView 스키마 정의
user_overall_progress_schema = extend_schema(
    summary="사용자의 전체 학습 진행률 조회",
    description="사용자의 전체 학습 진행률과 대분류(MajorCategory)별 학습 진행률을 반환합니다.",
    responses={
        200: OverallProgressSerializer,
        401: OpenApiResponse(description="인증되지 않은 사용자입니다."),
    }
)

# UserProgressDetailView 스키마 정의
user_progress_detail_schema = extend_schema(
    summary="특정 비디오의 학습 진행 상황 조회",
    description="사용자가 특정 비디오에 대해 학습한 진행 상황을 조회하는 API입니다.",
    parameters=[
        {
            "name": "video_id",
            "in": "path",
            "required": True,
            "description": "조회할 비디오의 ID",
            "schema": {"type": "integer"}
        }
    ],
    responses={
        200: VideoProgressSerializer,
        404: OpenApiResponse(description="해당 비디오 또는 수강 신청을 찾을 수 없습니다."),
    }
)
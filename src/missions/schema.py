from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .serializers import MissionSerializer, MultipleChoiceQuestionSerializer, MultipleChoiceSubmissionSerializer, DetailMultipleChoiceSubmissionSerializer, CodeSubmissionSerializer, SimpleSubmissionSerializer


# MissionViewSet의 스키마 정의
mission_list_schema = extend_schema(
    summary="Mission 목록 조회",
    description="모든 Mission 목록을 조회하거나 특정 MinorCategory에 속한 Mission만 필터링하여 반환합니다.",
    parameters=[
        OpenApiParameter(
            name="minor_category_id",
            description="특정 MinorCategory에 속한 Mission을 필터링하기 위한 ID",
            required=False,
            type=int,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=MissionSerializer(many=True),
            description="요청한 필터 기준에 맞는 Mission 목록을 반환합니다."
        ),
    }
)

mission_retrieve_schema = extend_schema(
    summary="특정 Mission 세부 정보 조회",
    description="특정 Mission의 세부 정보를 조회합니다. 사용자는 등록 상태가 active 또는 completed이거나, manager 또는 admin이어야 합니다.",
    responses={
        200: MissionSerializer,
        403: "접근 권한이 없습니다.",
        404: "Mission을 찾을 수 없습니다."
    }
)

mission_update_schema = extend_schema(
    summary="Mission 수정",
    description="기존 Mission의 정보를 수정합니다. 이 작업은 manager 또는 admin 권한이 있는 사용자만 할 수 있습니다.",
    responses={
        200: MissionSerializer,
        403: "접근 권한이 없습니다.",
        404: "Mission을 찾을 수 없습니다."
    }
)

mission_partial_update_schema = extend_schema(
    summary="Mission 부분 수정",
    description="기존 Mission의 일부 정보를 수정합니다. 이 작업은 manager 또는 admin 권한이 있는 사용자만 할 수 있습니다.",
    responses={
        200: MissionSerializer,
        403: "접근 권한이 없습니다.",
        404: "Mission을 찾을 수 없습니다."
    }
)

# MultipleChoiceQuestionViewSet 스키마 정의
multiple_choice_question_list_schema = extend_schema(
    summary="5지선다형 문제 목록 조회",
    description="모든 5지선다형 문제 목록을 조회하거나 특정 미션에 속한 문제만 필터링하여 반환합니다.",
    parameters=[
        OpenApiParameter(
            name="mission_id",
            description="특정 미션에 속한 문제를 필터링하기 위한 미션 ID.",
            required=False,
            type=int,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=MultipleChoiceQuestionSerializer(many=True),
            description="요청한 필터 기준에 맞는 문제 목록을 반환합니다."
        ),
    }
)

multiple_choice_question_retrieve_schema = extend_schema(
    summary="특정 5지선다형 문제 세부 정보 조회",
    description="특정 5지선다형 문제의 세부 정보를 조회합니다. 사용자는 등록 상태가 active 또는 completed이거나, manager 또는 admin이어야 합니다.",
    responses={
        200: MultipleChoiceQuestionSerializer,
        403: "접근 권한이 없습니다.",
        404: "해당 문제가 존재하지 않습니다."
    }
)

multiple_choice_question_update_schema = extend_schema(
    summary="5지선다형 문제 수정",
    description="기존 5지선다형 문제를 수정합니다. 이 작업은 manager 또는 admin 권한이 있는 사용자만 할 수 있습니다.",
    responses={
        200: MultipleChoiceQuestionSerializer,
        403: "접근 권한이 없습니다.",
        404: "해당 문제가 존재하지 않습니다."
    }
)

multiple_choice_question_partial_update_schema = extend_schema(
    summary="5지선다형 문제 부분 수정",
    description="기존 5지선다형 문제의 일부 정보를 수정합니다. 이 작업은 manager 또는 admin 권한이 있는 사용자만 할 수 있습니다.",
    responses={
        200: MultipleChoiceQuestionSerializer,
        403: "접근 권한이 없습니다.",
        404: "해당 문제가 존재하지 않습니다."
    }
)

multiple_choice_question_destroy_schema = extend_schema(
    summary="5지선다형 문제 삭제",
    description="특정 5지선다형 문제를 삭제합니다. 삭제 완료 시 성공 메시지를 반환하며, 존재하지 않는 문제일 경우 404 에러를 반환합니다.",
    responses={
        204: "문제가 성공적으로 삭제되었습니다.",
        404: "해당 문제가 존재하지 않습니다."
    }
)


# MultipleChoiceQuestionSubmissionAPIView 스키마 정의
multiple_choice_submission_schema = extend_schema(
    summary="5지선다형 문제 답안 제출 및 채점",
    description="사용자가 5지선다형 문제에 대한 답안을 제출하고, 제출된 답안이 맞았는지 여부를 반환합니다.",
    request=MultipleChoiceSubmissionSerializer,
    responses={
        201: OpenApiResponse(
            response={"message": "제출 완료", "is_correct": "boolean"},
            description="제출된 답안에 대한 채점 결과입니다."
        ),
        400: "잘못된 요청 데이터가 제출되었을 경우."
    }
)

# UserSubmissionListAPIView 스키마 정의
user_submission_list_schema = extend_schema(
    summary="사용자 제출 내역 조회",
    description="현재 로그인한 사용자의 모든 제출 내역을 조회합니다.",
    responses={200: DetailMultipleChoiceSubmissionSerializer(many=True)}
)

# AllSubmissionListAPIView 스키마 정의
all_submission_list_schema = extend_schema(
    summary="모든 사용자 제출 내역 조회",
    description="모든 사용자의 제출 내역을 조회합니다. manager 또는 admin 권한이 필요합니다.",
    responses={200: DetailMultipleChoiceSubmissionSerializer(many=True)}
)


# CodeSubmissionViewSet 스키마 정의

code_submission_list_schema = extend_schema(
    summary="코드 제출형 문제 목록 조회",
    description="특정 미션에 속한 코드 제출형 문제들을 필터링하여 목록을 반환합니다.",
    parameters=[
        OpenApiParameter(
            name="mission_id",
            description="필터링할 미션 ID. 이 값을 제공하면 해당 미션에 속한 문제들만 반환됩니다.",
            required=False,
            type=int,
        ),
    ],
    responses={
        200: OpenApiResponse(CodeSubmissionSerializer(many=True))
    }
)

code_submission_retrieve_schema = extend_schema(
    summary="특정 코드 제출형 문제 조회",
    description="특정 코드 제출형 문제의 세부 정보를 조회합니다.",
    responses={
        200: CodeSubmissionSerializer,
        403: "접근 권한이 없습니다.",
        404: "해당 문제가 존재하지 않습니다."
    }
)

code_submission_update_schema = extend_schema(
    summary="코드 제출형 문제 수정",
    description="기존 코드 제출형 문제의 정보를 수정합니다.",
    responses={
        200: CodeSubmissionSerializer,
        403: "접근 권한이 없습니다.",
        404: "해당 문제가 존재하지 않습니다."
    }
)

code_submission_destroy_schema = extend_schema(
    summary="코드 제출형 문제 삭제",
    description="특정 코드 제출형 문제를 삭제합니다.",
    responses={
        204: "문제가 성공적으로 삭제되었습니다.",
        404: "해당 문제가 존재하지 않습니다."
    }
)

# CodeSubmissionEvaluationAPIView 스키마 정의
code_submission_evaluation_schema = extend_schema(
    summary="제출된 코드 채점",
    description="사용자가 제출한 코드를 미리 정의된 시간 및 메모리 제한 내에서 채점하고 결과를 반환합니다.",
    request={
        "type": "object",
        "properties": {
            "submitted_code": {"type": "string", "description": "제출된 코드"}
        },
        "required": ["submitted_code"]
    },
    responses={
        200: OpenApiResponse(
            response={
                "message": "채점 완료",
                "test_results": "테스트 결과 리스트",
                "is_passed": "채점 통과 여부 (boolean)"
            },
            description="채점 결과 및 통과 여부를 포함한 응답."
        ),
        400: "잘못된 요청 데이터 (코드 누락 등).",
        404: "해당 코드 제출형 문제가 존재하지 않음."
    }
)

# UserCodeSubmissionListAPIView 및 AllCodeSubmissionListAPIView 스키마 정의
user_code_submission_list_schema = extend_schema(
    summary="사용자 코드 제출 내역 조회",
    description="현재 로그인한 사용자의 제출 내역을 조회합니다.",
    responses={200: SimpleSubmissionSerializer(many=True)}
)

all_code_submission_list_schema = extend_schema(
    summary="모든 사용자 코드 제출 내역 조회",
    description="모든 사용자의 제출 내역을 조회합니다.",
    responses={200: SimpleSubmissionSerializer(many=True)}
)
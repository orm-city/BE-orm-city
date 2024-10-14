from drf_spectacular.utils import extend_schema
from .serializers import MajorCategorySerializer, MinorCategorySerializer, EnrollmentSerializer

# MajorCategoryViewSet 스키마 정의
major_category_schemas = {
    'list': extend_schema(
        summary="MajorCategory 목록 조회",
        description="모든 MajorCategory 항목을 반환합니다.",
        responses={200: MajorCategorySerializer(many=True)},
    ),
    'retrieve': extend_schema(
        summary="MajorCategory 세부 정보 조회",
        description="특정 MajorCategory의 세부 정보를 반환하고 해당 MajorCategory에 포함된 비디오 통계를 제공합니다.",
        responses={200: MajorCategorySerializer},
    ),
    'create': extend_schema(tags=["courses"]),
    'update': extend_schema(tags=["courses"]),
    'partial_update': extend_schema(tags=["courses"]),
    'destroy': extend_schema(tags=["courses"]),
    'details': extend_schema(tags=["courses"]),
}

# MinorCategoryViewSet 스키마 정의
minor_category_schemas = {
    'list': extend_schema(
        summary="MinorCategory 목록 조회",
        description="특정 MajorCategory에 속한 MinorCategory 목록을 조회합니다.",
        responses={200: MinorCategorySerializer(many=True)},
    ),
    'retrieve': extend_schema(
        summary="MinorCategory 세부 정보 조회",
        description="특정 MinorCategory의 세부 정보를 반환합니다.",
        responses={200: MinorCategorySerializer},
    ),
    'create': extend_schema(tags=["courses"]),
    'update': extend_schema(tags=["courses"]),
    'partial_update': extend_schema(tags=["courses"]),
    'destroy': extend_schema(tags=["courses"]),
}

# EnrollmentViewSet 스키마 정의
enrollment_schemas = {
    'list': extend_schema(
        summary="수강 신청 목록 조회",
        description="현재 사용자의 수강 신청 목록을 반환합니다.",
        responses={200: EnrollmentSerializer(many=True)},
    ),
    'retrieve': extend_schema(
        summary="수강 신청 세부 정보 조회",
        description="특정 수강 신청의 세부 정보를 반환합니다.",
        responses={200: EnrollmentSerializer},
    ),
    'create': extend_schema(
        summary="수강 신청 생성",
        description="새로운 수강 신청을 생성합니다. 학생만 수강 신청할 수 있습니다.",
        request=EnrollmentSerializer,
        responses={201: EnrollmentSerializer, 400: "잘못된 요청 데이터"},
    ),
    'update': extend_schema(tags=["courses"]),
    'partial_update': extend_schema(tags=["courses"]),
    'destroy': extend_schema(tags=["courses"]),
    'active_enrollments': extend_schema(tags=["courses"]),
    'complete_enrollment': extend_schema(
        summary="수강 신청 완료",
        description="특정 수강 신청을 완료 상태로 변경합니다.",
        request=None,
        responses={200: "수강 완료 성공", 400: "수강 완료 실패"},
    ),
}

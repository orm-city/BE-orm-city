from drf_spectacular.utils import extend_schema, extend_schema_field
from drf_spectacular.types import OpenApiTypes

from rest_framework import serializers

from .serializers import ManagerCreationSerializer, UserRegistrationSerializer,  UserLoginSerializer, UserActivitySerializer, UserSerializer


paginated_response_schema = extend_schema_field(
    serializers.Serializer(
        {
            "count": OpenApiTypes.INT,  # 총 항목 수
            "next": OpenApiTypes.URI,   # 다음 페이지의 URI
            "previous": OpenApiTypes.URI,  # 이전 페이지의 URI
            "results": OpenApiTypes.OBJECT  # 페이지 내의 결과 리스트
        }
    )
)

user_list_schema = extend_schema(
    summary="사용자 목록 조회",
    description="요청한 사용자의 권한에 따라 사용자 목록을 필터링하여 반환합니다. 관리자는 모든 사용자를 조회할 수 있으며, 매니저는 학생만 조회할 수 있습니다.",
    responses={200: UserSerializer(many=True)},
)

user_retrieve_schema = extend_schema(
    summary="사용자 세부 정보 조회",
    description="특정 사용자의 세부 정보를 조회합니다. 인증된 사용자는 자신의 정보를 조회할 수 있습니다.",
    responses={200: UserSerializer},
)

user_create_schema = extend_schema(
    summary="사용자 생성",
    description="새로운 사용자를 생성합니다. 이 작업은 관리자만 수행할 수 있습니다.",
    request=UserSerializer,
    responses={201: UserSerializer},
)

user_update_schema = extend_schema(
    summary="사용자 수정",
    description="기존 사용자의 정보를 수정합니다. 이 작업은 관리자만 수행할 수 있습니다.",
    request=UserSerializer,
    responses={200: UserSerializer},
)

user_partial_update_schema = extend_schema(
    summary="사용자 부분 수정",
    description="기존 사용자의 일부 정보를 수정합니다. 이 작업은 관리자만 수행할 수 있습니다.",
    request=UserSerializer,
    responses={200: UserSerializer},
)

user_destroy_schema = extend_schema(
    summary="사용자 삭제",
    description="특정 사용자를 삭제합니다. 이 작업은 관리자만 수행할 수 있습니다.",
    responses={204: None},
)


register_view_schema = extend_schema(
    summary="사용자 등록",
    description="새로운 사용자를 등록하고, 해당 사용자 정보와 JWT 토큰(액세스 토큰, 리프레시 토큰)을 반환합니다.",
    request=UserRegistrationSerializer,
    responses={
        201: UserSerializer,  # 사용자 정보와 함께 반환
        400: "잘못된 요청입니다. 입력 데이터를 확인하세요.",
    }
)

# LoginView에 대한 스키마 정의
login_view_schema = extend_schema(
    summary="사용자 로그인",
    description="사용자가 로그인할 수 있도록 처리하며, 로그인 성공 시 사용자 정보와 JWT 토큰(액세스 토큰, 리프레시 토큰)을 반환합니다.",
    request=UserLoginSerializer,
    responses={
        200: UserSerializer,  # 사용자 정보와 JWT 토큰이 포함된 응답
        400: "잘못된 로그인 정보입니다.",
    }
)

# LogoutView에 대한 스키마 정의
logout_view_schema = extend_schema(
    summary="사용자 로그아웃",
    description="사용자가 로그아웃할 수 있도록 처리하며, 리프레시 토큰을 블랙리스트에 추가하여 이후 사용할 수 없도록 합니다.",
    request=None,  # 로그아웃 요청은 리프레시 토큰을 포함한 데이터
    responses={
        200: "로그아웃 성공 메시지",
        400: "잘못된 요청 데이터입니다.",
    }
)

# UserProfileView 스키마 정의
user_profile_retrieve_schema = extend_schema(
    summary="사용자 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다.",
    responses={200: UserSerializer}
)

user_profile_update_schema = extend_schema(
    summary="사용자 프로필 수정",
    description="현재 로그인한 사용자의 프로필 정보를 수정합니다.",
    request=UserSerializer,
    responses={200: UserSerializer}
)

# UserActivityListView 스키마 정의
user_activity_list_schema = extend_schema(
    summary="사용자 활동 기록 조회",
    description="현재 로그인한 사용자의 활동 기록을 조회합니다.",
    responses={200: UserActivitySerializer(many=True)}
)

delete_account_schema = extend_schema(
    summary="계정 삭제",
    description="현재 로그인한 사용자의 계정을 삭제합니다. 삭제된 계정은 복구할 수 없습니다.",
    responses={
        204: "계정이 성공적으로 삭제되었습니다.",
        401: "인증되지 않은 사용자가 계정 삭제를 시도할 경우."
    }
)

manager_creation_schema = extend_schema(
    summary="매니저 계정 생성",
    description="새로운 매니저 계정을 생성합니다. 이 작업은 관리자만 수행할 수 있습니다.",
    request=ManagerCreationSerializer,  # 요청 데이터 정의
    responses={
        201: UserSerializer,  # 성공 시 반환될 사용자 정보
        400: "잘못된 요청 데이터. 유효성 검사를 통과하지 못한 경우 오류 메시지 반환."
    }
)

change_user_role_schema = extend_schema(
    summary="사용자 역할 변경",
    description="관리자가 특정 사용자의 역할을 변경합니다. 변경 가능한 역할은 'student' 또는 'manager'입니다.",
    request={
        "type": "object",
        "properties": {
            "role": {"type": "string", "description": "변경할 역할 ('student' 또는 'manager')"}
        },
        "required": ["role"]
    },
    responses={
        200: UserSerializer,
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
        404: {"type": "object", "properties": {"error": {"type": "string"}}}
    }
)

role_check_schema = extend_schema(
    summary="사용자 역할 확인",
    description="현재 로그인한 사용자의 역할 정보를 반환합니다.",
    responses={
        200: {"type": "object", "properties": {"role": {"type": "string"}}}
    }
)
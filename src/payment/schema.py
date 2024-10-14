from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .serializers import UserProgressSerializer, OverallProgressSerializer, VideoProgressSerializer

# PaymentInfoAPIView 스키마 정의
payment_info_schema = extend_schema(
    summary="아임포트 결제정보 조회",
    description="선택한 대분류 수강 카테고리와 수강 금액 정보를 아임포트 결제창에 전달하기 위한 정보를 제공합니다.",
    parameters=[
        OpenApiParameter(
            name="major_category_id",
            description="대분류 카테고리의 ID. 이 값을 제공하면 해당 수강 카테고리의 결제 정보를 반환합니다.",
            required=True,
            type=int,
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "major_category_id": {"type": "integer", "description": "대분류 카테고리의 ID"},
                "major_category_name": {"type": "string", "description": "대분류 카테고리 이름"},
                "major_category_price": {"type": "number", "description": "대분류 카테고리의 수강 가격"},
                "user_id": {"type": "integer", "description": "사용자 ID"},
                "imp_key": {"type": "string", "description": "아임포트 결제 API 키"},
            },
        },
        404: {"description": "해당 대분류 카테고리를 찾을 수 없습니다."},
    },
)


# PaymentCompleteAPIView 스키마 정의
payment_complete_schema = extend_schema(
    summary="결제 생성 및 수강 등록",
    description="사용자가 결제를 완료하면 해당 결제 정보와 수강 등록 정보를 생성합니다.",
    request={
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "결제 사용자 ID"},
            "imp_uid": {"type": "string", "description": "아임포트에서 제공된 결제 고유 ID"},
            "merchant_uid": {"type": "string", "description": "가맹점 고유 주문 번호"},
            "major_category_id": {"type": "integer", "description": "결제하려는 수강 카테고리의 ID"},
            "total_amount": {"type": "number", "description": "결제 금액"},
        },
        "required": [
            "user_id",
            "imp_uid",
            "merchant_uid",
            "major_category_id",
            "total_amount",
        ],
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "결제 및 수강 등록 완료 메시지"},
                "payment_id": {"type": "integer", "description": "생성된 결제 정보의 ID"},
                "enrollment_id": {"type": "integer", "description": "생성된 수강 등록 정보의 ID"},
                "status": {"type": "string", "description": "결제 상태"},
                "refund_deadline": {"type": "string", "format": "date-time", "description": "환불 가능 기한"},
            },
        },
        400: {"description": "잘못된 결제 정보 혹은 중복 결제."},
        404: {"description": "사용자 또는 수강 카테고리 정보가 확인되지 않음."},
    },
)


# UserPaymentsView 스키마 정의
user_payments_schema = extend_schema(
    summary="사용자 결제 내역 조회",
    description="사용자의 모든 결제 내역을 반환합니다. 각 결제는 환불 가능 여부도 포함합니다.",
    responses={
        200: OpenApiResponse(
            response={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "결제 ID"},
                        "amount": {"type": "number", "description": "결제 금액"},
                        "date": {"type": "string", "format": "date-time", "description": "결제 날짜"},
                        "status": {"type": "string", "description": "결제 상태"},
                        "is_refundable": {"type": "boolean", "description": "환불 가능 여부"},
                        "days_since_payment": {"type": "integer", "description": "결제 후 경과 일수"},
                        "major_category": {"type": "string", "description": "결제한 대분류 카테고리"},
                    },
                },
            },
            description="결제 내역 목록이 성공적으로 반환됩니다."
        ),
        401: {"description": "인증되지 않은 사용자"},
    }
)

# PaymentDetailView 스키마 정의
payment_detail_schema = extend_schema(
    summary="결제 세부 정보 조회",
    description="특정 결제의 세부 정보를 조회하고 반환합니다.",
    parameters=[
        OpenApiParameter(
            name="payment_id",
            description="조회할 결제의 ID",
            required=True,
            type=int,
        ),
    ],
    responses={
        200: PaymentDetailSerializer,
        404: {"description": "결제 정보를 찾을 수 없습니다."},
        401: {"description": "인증되지 않은 사용자"},
    }
)


# RefundAPIView 스키마 정의
refund_api_view_schema = extend_schema(
    summary="결제 환불 요청",
    description="사용자의 결제 내역 중 특정 결제에 대해 환불을 요청합니다. 성공 시 처리 결과를 반환합니다.",
    parameters=[
        OpenApiParameter(
            name="payment_id",
            description="환불할 결제의 ID",
            required=True,
            type=int,
        ),
    ],
    request={
        "type": "object",
        "properties": {
            "payment_id": {"type": "integer", "description": "환불을 요청할 결제의 ID"},
        },
        "required": ["payment_id"],
    },
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "환불이 성공적으로 처리되었습니다."},
                },
            },
            description="환불이 성공적으로 처리된 경우"
        ),
        400: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "환불 처리에 실패했습니다."},
                },
            },
            description="잘못된 요청이거나 환불 실패한 경우"
        ),
        404: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "결제 정보를 찾을 수 없습니다."},
                },
            },
            description="결제 정보를 찾을 수 없거나 결제가 존재하지 않을 때"
        ),
        503: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "결제 시스템 연결에 실패했습니다."},
                },
            },
            description="결제 시스템 연결 실패"
        ),
    },
)



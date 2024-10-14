from drf_spectacular.utils import extend_schema

from .serializers import UserSerializer  # 필요 시 다른 시리얼라이저도 추가

from rest_framework import status

# AvailableCertificatesAPIView 스키마 정의
available_certificates_schema = extend_schema(
    summary="사용자가 발급받을 수 있는 인증서 목록 조회",
    description="현재 사용자가 발급받을 수 있는 Minor 및 Major 카테고리의 인증서를 조회합니다.",
    responses={
        200: {
            "type": "object",
            "properties": {
                "available_minor_certificates": {"type": "array", "items": {"type": "string"}},
                "available_major_certificates": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
)

# CertificatePreviewAPIView 스키마 정의
certificate_preview_schema = extend_schema(
    summary="인증서 미리보기 이미지 생성",
    description="사용자의 인증서를 이미지 형식으로 생성하고 이를 미리보기로 반환합니다. PNG 형식으로 제공됩니다.",
    responses={
        200: {"content": {"image/png": {}}},
        404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        500: {"type": "object", "properties": {"detail": {"type": "string"}}}
    }
)

# CertificateDownloadAPIView 스키마 정의
certificate_download_schema = extend_schema(
    summary="인증서 PDF 다운로드",
    description="사용자의 인증서를 PDF 형식으로 생성하여 다운로드할 수 있습니다.",
    responses={
        200: {"content": {"application/pdf": {}}},
        404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        500: {"type": "object", "properties": {"detail": {"type": "string"}}}
    }
)

# VerifyCertificateAPIView 스키마 정의
verify_certificate_schema = extend_schema(
    summary="인증서 유효성 검증",
    description="주어진 인증서 ID를 통해 해당 인증서의 유효성을 확인하고 복호화된 데이터를 반환합니다.",
    responses={
        200: {
            "type": "object",
            "properties": {
                "certificate_id": {"type": "string"},
                "decrypted_data": {"type": "object"},
                "is_valid": {"type": "boolean"}
            }
        },
        400: {"type": "object", "properties": {"detail": {"type": "string"}, "error": {"type": "string"}}},
        404: {"type": "object", "properties": {"detail": {"type": "string"}}}
    }
)

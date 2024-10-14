from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from certificates.models import Certificate
from certificates.permissions import IsCertificateOwner
from certificates.services import (
    decrypt_certificate_data,
    generate_certificate_image,
    generate_certificate_pdf,
    get_course_name,
    get_available_certificates,
    get_course_model,
)

from .schema import (
    available_certificates_schema,
    certificate_preview_schema,
    certificate_download_schema,
    verify_certificate_schema
) 


class AvailableCertificatesAPIView(APIView):
    """
    사용자가 완료한 MinorCategory와 MajorCategory의 인증서를 조회하는 API 뷰입니다.
    """

    @available_certificates_schema
    def get(self, request):
        """
        사용자가 발급받을 수 있는 Minor 및 Major 카테고리의 인증서를 조회합니다.

        Args:
            request (HttpRequest): 사용자 요청 객체.

        Returns:
            Response: 사용자가 완료한 인증서 목록.
        """
        user = request.user
        available_minor, available_major = get_available_certificates(user)

        return Response(
            {
                "available_minor_certificates": [
                    minor.name for minor in available_minor
                ],
                "available_major_certificates": [
                    major.name for major in available_major
                ],
            }
        )


class CertificatePreviewAPIView(APIView):
    """
    사용자의 인증서를 이미지로 생성하고, 이를 미리보기 형식으로 제공하는 API 뷰입니다.
    """

    permission_classes = [IsAuthenticated, IsCertificateOwner]

    @certificate_preview_schema
    def get(self, request, course_type=None, course_id=None):
        """
        GET 요청을 처리하여 인증서의 PNG 이미지를 생성합니다.

        Args:
            request (HttpRequest): 요청 객체.
            course_type (str): 코스의 유형을 나타내는 문자열.
            course_id (int): 코스의 ID.

        Returns:
            HttpResponse: 생성된 인증서의 PNG 이미지를 반환합니다. 성공 시 HTTP 200 응답을 반환하며, 코스를 찾지 못하거나 이미지 생성 중 오류가 발생한 경우 각각 HTTP 404, 500 응답을 반환합니다.
        """
        user = request.user

        try:
            course_name = get_course_name(course_id, course_type)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        try:
            image_buffer = generate_certificate_image(user.username, course_name)
        except Exception:
            return Response({"detail": "인증서 생성 중 오류 발생"}, status=500)

        response = HttpResponse(image_buffer, content_type="image/png")
        return response


class CertificateDownloadAPIView(APIView):
    """
    사용자의 인증서를 PDF 형식으로 다운로드할 수 있는 API 뷰입니다.
    """

    permission_classes = [IsAuthenticated, IsCertificateOwner]

    @certificate_download_schema
    def get(self, request, course_type=None, course_id=None):
        """
        GET 요청을 처리하여 인증서를 PDF 형식으로 다운로드합니다.

        Args:
            request (HttpRequest): 요청 객체.
            course_type (str): 코스의 유형을 나타내는 문자열.
            course_id (int): 코스의 ID.

        Returns:
            HttpResponse: 생성된 인증서의 PDF를 반환합니다.
        """
        user = request.user

        try:
            course_name = get_course_name(course_id, course_type)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        certificate, created = Certificate.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(
                get_course_model(course_type)
            ),
            object_id=course_id,
        )

        if created:
            certificate.generate_certificate()

        try:
            pdf_buffer = generate_certificate_pdf(
                user.username, course_name, certificate.certificate_id
            )
        except Exception:
            return Response({"detail": "인증서 생성 중 오류 발생"}, status=500)

        response = HttpResponse(pdf_buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="certificate_{course_id}_{course_type}.pdf"'
        )
        return response


class VerifyCertificateAPIView(APIView):
    """
    주어진 인증서 ID를 통해 수료증의 유효성을 확인하는 API 뷰입니다.
    """

    permission_classes = [AllowAny]

    @verify_certificate_schema 
    def get(self, request, certificate_id):
        """
        GET 요청을 통해 인증서 ID에 해당하는 인증서의 유효성을 확인합니다.

        Args:
            request (HttpRequest): 요청 객체.
            certificate_id (uuid.UUID): 인증서의 고유 ID.

        Returns:
            Response: 인증서의 유효성 및 복호화된 데이터를 반환합니다.
        """
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

        try:
            decrypted_data = decrypt_certificate_data(certificate.encrypted_data)

            return Response(
                {
                    "certificate_id": certificate.certificate_id,
                    "decrypted_data": decrypted_data,
                    "is_valid": True,
                },
                status=200,
            )
        except Exception as e:
            return Response(
                {"detail": "Invalid certificate data", "error": str(e)}, status=400
            )

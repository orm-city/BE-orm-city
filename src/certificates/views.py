from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

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
from courses.serializers import (
    SimpleMajorCategorySerializer,
    SimpleMinorCategorySerializer,
)


class AvailableCertificatesAPIView(APIView):
    def get(self, request):
        user = request.user
        available_minor, available_major = get_available_certificates(user)

        # 새로운 간단한 시리얼라이저를 사용하여 필요한 데이터만 반환
        return Response(
            {
                "available_major_certificates": SimpleMajorCategorySerializer(
                    available_major, many=True
                ).data,
                "available_minor_certificates": SimpleMinorCategorySerializer(
                    available_minor, many=True
                ).data,
            }
        )


class CertificatePreviewAPIView(APIView):
    """
    사용자의 인증서를 이미지로 생성하고, 이를 미리보기 형식으로 제공하는 API 뷰입니다.
    """

    permission_classes = [IsAuthenticated, IsCertificateOwner]

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
    permission_classes = [IsAuthenticated, IsCertificateOwner]

    def get(self, request, course_type=None, course_id=None):
        user = request.user

        try:
            course_name = get_course_name(course_id, course_type)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        # 수료증 발급 또는 기존 수료증 가져오기
        certificate, created = Certificate.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(
                get_course_model(course_type)
            ),
            object_id=course_id,
        )

        # 인증서가 새로 생성되었을 때 암호화된 데이터를 저장
        if created:
            certificate.generate_certificate()  # 수료증 데이터 암호화 및 저장

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
    permission_classes = [AllowAny]

    def get(self, request, certificate_id):
        # 수료증을 DB에서 조회
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

        try:
            # 암호화된 수료증 데이터를 복호화
            decrypted_data = decrypt_certificate_data(certificate.encrypted_data)

            # 복호화된 데이터를 반환
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

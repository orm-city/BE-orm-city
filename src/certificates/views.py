from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse

from certificates.services import (
    generate_certificate_image,
    generate_certificate_pdf,
    get_course_name,
)


class CertificatePreviewAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, course_type=None, course_id=None):
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
    permission_classes = [AllowAny]

    def get(self, request, course_type=None, course_id=None):
        user = request.user

        try:
            course_name = get_course_name(course_id, course_type)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        try:
            pdf_buffer = generate_certificate_pdf(user.username, course_name)
        except Exception:
            return Response({"detail": "인증서 생성 중 오류 발생"}, status=500)

        response = HttpResponse(pdf_buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="certificate_{course_id}_{course_type}.pdf"'
        )
        return response

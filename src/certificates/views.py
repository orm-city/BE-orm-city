from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from .services import (
    get_course_name,
    generate_certificate_image,
    generate_certificate_pdf,
)


class CertificateViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(
        detail=False,
        methods=["get"],
        url_path="preview/(?P<course_type>[^/]+)/(?P<course_id>[0-9]+)",
    )
    def preview(self, request, course_type=None, course_id=None):
        user = request.user

        try:
            course_name = get_course_name(course_id, course_type)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        try:
            image_buffer = generate_certificate_image(user.username, course_name)
        except Exception as e:
            print(f"이미지 생성 중 오류: {str(e)}")
            return Response({"detail": "인증서 생성 중 오류 발생"}, status=500)

        response = HttpResponse(image_buffer, content_type="image/png")
        return response

    @action(
        detail=False,
        methods=["get"],
        url_path="download/(?P<course_type>[^/]+)/(?P<course_id>[0-9]+)",
    )
    def download(self, request, course_type=None, course_id=None):
        user = request.user

        try:
            course_name = get_course_name(course_id, course_type)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        try:
            pdf_buffer = generate_certificate_pdf(user.username, course_name)
        except Exception as e:
            print(f"PDF 생성 중 오류: {str(e)}")
            return Response({"detail": "인증서 생성 중 오류 발생"}, status=500)

        response = HttpResponse(pdf_buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="certificate_{course_id}_{course_type}.pdf"'
        )
        return response

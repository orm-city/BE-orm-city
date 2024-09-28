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
    """
    사용자의 인증서를 이미지로 생성하고, 이를 미리보기 형식으로 제공하는 API 뷰입니다.
    """

    permission_classes = [AllowAny]  # TODO: 바꿔야함

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
    인증서를 PDF 파일로 생성하고, 이를 다운로드할 수 있도록 제공하는 API 뷰입니다.
    """

    permission_classes = [AllowAny]  # TODO: 바꿔야함

    def get(self, request, course_type=None, course_id=None):
        """
        GET 요청을 처리하여 인증서의 PDF 파일을 생성하고, 이를 첨부파일로 제공합니다.

        Args:
            request (HttpRequest): 요청 객체.
            course_type (str): 코스의 유형을 나타내는 문자열.
            course_id (int): 코스의 ID.

        Returns:
            HttpResponse: 생성된 인증서의 PDF 파일을 첨부파일로 반환합니다. 성공 시 HTTP 200 응답을 반환하며, 코스를 찾지 못하거나 PDF 생성 중 오류가 발생한 경우 각각 HTTP 404, 500 응답을 반환합니다.
        """
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

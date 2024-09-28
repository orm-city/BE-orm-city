import os
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
from courses.models import MinorCategory, MajorCategory
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model


class CertificatePreviewView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, course_id, course_type):
        # user = request.user
        User = get_user_model()
        user = User.objects.get(username="kyungmin")

        if course_type == "minor":
            try:
                course_name = MinorCategory.objects.get(id=course_id).name
            except MinorCategory.DoesNotExist:
                return Response(
                    {"detail": "소분류 과정이 존재하지 않습니다."}, status=404
                )
        elif course_type == "major":
            try:
                course_name = MajorCategory.objects.get(id=course_id).name
            except MajorCategory.DoesNotExist:
                return Response(
                    {"detail": "대분류 과정이 존재하지 않습니다."}, status=404
                )
        else:
            return Response({"detail": "유효하지 않은 과정 유형입니다."}, status=400)

        try:
            image_buffer = self.generate_certificate_image(user.username, course_name)
        except Exception as e:
            print(f"이미지 생성 중 오류: {str(e)}")
            return Response({"detail": "인증서 생성 중 오류 발생"}, status=500)

        response = HttpResponse(image_buffer, content_type="image/png")
        return response

    def generate_certificate_image(self, user_name, course_name):
        # 이미지와 폰트 경로 설정
        image_path = os.path.join(
            settings.STATICFILES_DIRS[0], "img", "certificate_template.png"
        )
        font_path = os.path.join(
            settings.STATICFILES_DIRS[0], "fonts", "SongMyung-Regular.ttf"
        )

        # 이미지와 폰트 파일 존재 여부 확인
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"폰트 파일을 찾을 수 없습니다: {font_path}")

        # 디버깅: 폰트 로드 확인
        try:
            name_font = ImageFont.truetype(font_path, 90)
            course_font = ImageFont.truetype(font_path, 40)
        except Exception as e:
            raise RuntimeError(f"폰트 로드 중 오류 발생: {str(e)}")

        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        name_text_color = (191, 133, 46)
        course_text_color = (5, 5, 55)
        name_position_y = 750
        course_1_position_y = 950
        course_2_position_y = 1050
        course_3_position_y = 1150

        # 텍스트 중앙 정렬을 위한 너비 계산
        name_text = user_name
        course_text_1 = "ORMCITY에서 제공하는"
        course_text_2 = f"{course_name}을(를) 수료하였기에"
        course_text_3 = "이 증서를 드립니다."

        name_text_width = (
            draw.textbbox((0, 0), name_text, font=name_font)[2]
            - draw.textbbox((0, 0), name_text, font=name_font)[0]
        )
        course_text_1_width = (
            draw.textbbox((0, 0), course_text_1, font=course_font)[2]
            - draw.textbbox((0, 0), course_text_1, font=course_font)[0]
        )
        course_text_2_width = (
            draw.textbbox((0, 0), course_text_2, font=course_font)[2]
            - draw.textbbox((0, 0), course_text_2, font=course_font)[0]
        )
        course_text_3_width = (
            draw.textbbox((0, 0), course_text_3, font=course_font)[2]
            - draw.textbbox((0, 0), course_text_3, font=course_font)[0]
        )

        # 이미지 중앙에 맞게 텍스트 위치 설정
        name_position_x = (image.width - name_text_width) // 2
        course_1_position_x = (image.width - course_text_1_width) // 2
        course_2_position_x = (image.width - course_text_2_width) // 2
        course_3_position_x = (image.width - course_text_3_width) // 2

        # 텍스트 이미지에 그리기
        draw.text(
            (name_position_x, name_position_y),
            name_text,
            font=name_font,
            fill=name_text_color,
        )
        draw.text(
            (course_1_position_x, course_1_position_y),
            course_text_1,
            font=course_font,
            fill=course_text_color,
        )
        draw.text(
            (course_2_position_x, course_2_position_y),
            course_text_2,
            font=course_font,
            fill=course_text_color,
        )
        draw.text(
            (course_3_position_x, course_3_position_y),
            course_text_3,
            font=course_font,
            fill=course_text_color,
        )

        # 이미지를 버퍼에 저장
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer


class CertificateDownloadView(APIView):
    """
    인증서를 PDF로 다운로드하는 API 뷰
    """

    permission_classes = [AllowAny]

    def get(self, request, course_id, course_type):
        # user = request.user
        User = get_user_model()
        user = User.objects.get(username="kyungmin")

        if course_type == "minor":
            course_name = MinorCategory.objects.get(id=course_id).name
        elif course_type == "major":
            course_name = MajorCategory.objects.get(id=course_id).name
        else:
            return Response({"detail": "유효하지 않은 과정 유형입니다."}, status=400)

        pdf_buffer = self.generate_certificate_pdf(user.username, course_name)

        response = HttpResponse(pdf_buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="certificate_{course_id}_{course_type}.pdf"'
        )
        return response

    def generate_certificate_pdf(self, user_name, course_name):
        """
        주어진 사용자 이름과 과정 이름을 바탕으로 인증서를 PDF로 생성
        """
        # 이미지와 폰트 경로 설정
        image_path = os.path.join(
            settings.STATICFILES_DIRS[0], "img", "certificate_template.png"
        )
        font_path = os.path.join(
            settings.STATICFILES_DIRS[0], "fonts", "SongMyung-Regular.ttf"
        )

        # 이미지와 폰트 파일 존재 여부 확인
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"폰트 파일을 찾을 수 없습니다: {font_path}")

        # 디버깅: 폰트 로드 확인
        try:
            name_font = ImageFont.truetype(font_path, 90)
            course_font = ImageFont.truetype(font_path, 40)
        except Exception as e:
            raise RuntimeError(f"폰트 로드 중 오류 발생: {str(e)}")

        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        name_text_color = (191, 133, 46)
        course_text_color = (5, 5, 55)
        name_position_y = 750
        course_1_position_y = 950
        course_2_position_y = 1050
        course_3_position_y = 1150

        # 텍스트 중앙 정렬을 위한 너비 계산
        name_text = user_name
        course_text_1 = "ORMCITY에서 제공하는"
        course_text_2 = f"{course_name}을(를) 수료하였기에"
        course_text_3 = "이 증서를 드립니다."

        name_text_width = (
            draw.textbbox((0, 0), name_text, font=name_font)[2]
            - draw.textbbox((0, 0), name_text, font=name_font)[0]
        )
        course_text_1_width = (
            draw.textbbox((0, 0), course_text_1, font=course_font)[2]
            - draw.textbbox((0, 0), course_text_1, font=course_font)[0]
        )
        course_text_2_width = (
            draw.textbbox((0, 0), course_text_2, font=course_font)[2]
            - draw.textbbox((0, 0), course_text_2, font=course_font)[0]
        )
        course_text_3_width = (
            draw.textbbox((0, 0), course_text_3, font=course_font)[2]
            - draw.textbbox((0, 0), course_text_3, font=course_font)[0]
        )

        # 이미지 중앙에 맞게 텍스트 위치 설정
        name_position_x = (image.width - name_text_width) // 2
        course_1_position_x = (image.width - course_text_1_width) // 2
        course_2_position_x = (image.width - course_text_2_width) // 2
        course_3_position_x = (image.width - course_text_3_width) // 2

        # 텍스트 이미지에 그리기
        draw.text(
            (name_position_x, name_position_y),
            name_text,
            font=name_font,
            fill=name_text_color,
        )
        draw.text(
            (course_1_position_x, course_1_position_y),
            course_text_1,
            font=course_font,
            fill=course_text_color,
        )
        draw.text(
            (course_2_position_x, course_2_position_y),
            course_text_2,
            font=course_font,
            fill=course_text_color,
        )
        draw.text(
            (course_3_position_x, course_3_position_y),
            course_text_3,
            font=course_font,
            fill=course_text_color,
        )

        buffer = BytesIO()
        image.save(buffer, format="PDF")
        buffer.seek(0)

        return buffer

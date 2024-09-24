from django.db import models
from django.conf import settings
from io import BytesIO
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import os


class Certificate(models.Model):
    """
    수료증에 대한 모델 정의
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="수료증을 받은 사용자",
    )
    major_category = models.ForeignKey(
        "MajorCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="수료한 대분류 코스",
    )
    minor_category = models.ForeignKey(
        "MinorCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="수료한 소분류 코스",
    )
    issue_date = models.DateTimeField(auto_now_add=True, help_text="수료증 발급일")
    certificate_id = models.CharField(
        max_length=100, unique=True, help_text="수료증 고유 ID"
    )

    def __str__(self):
        if self.major_category:
            return f"{self.user.username} - {self.major_category.title} - {self.certificate_id}"
        elif self.minor_category:
            return f"{self.user.username} - {self.minor_category.title} - {self.certificate_id}"
        return f"{self.user.username} - {self.certificate_id}"

    def generate_certificate_pdf(self):
        """
        수료증을 PDF 형식으로 동적으로 생성하여 반환하는 메서드
        """
        try:
            # 배경 이미지 로드
            image_path = os.path.join(
                settings.BASE_DIR, "path_to_image", "크림색 및 금색 간소한 인증서.png"
            )
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)

            # 폰트 설정
            font_path = os.path.join(
                settings.BASE_DIR, "path_to_fonts", "DejaVuSans-Bold.ttf"
            )
            name_font = ImageFont.truetype(font_path, 60)
            course_font = ImageFont.truetype(font_path, 40)

            # 사용자 이름과 코스 이름 추가
            user_name = self.user.username
            course_name = (
                self.major_category.title
                if self.major_category
                else self.minor_category.title
                if self.minor_category
                else ""
            )
            # 텍스트 위치 조정 - 동적으로 중앙에 배치
            text_width, _ = draw.textsize(user_name, font=name_font)
            name_position = ((image.width - text_width) // 2, 300)

            text_width, _ = draw.textsize(
                f"{course_name}을 수료하였기에", font=course_font
            )
            course_position = ((image.width - text_width) // 2, 500)

            draw.text(name_position, user_name, font=name_font, fill="brown")
            draw.text(
                course_position,
                f"{course_name}을 수료하였기에",
                font=course_font,
                fill="brown",
            )

            # 이미지를 PDF로 변환
            buffer = BytesIO()
            image.save(buffer, format="PDF")
            buffer.seek(0)

            return buffer

        except Exception as e:
            # 예외 발생 시 로그 기록 또는 오류 처리
            print(f"PDF 생성 중 오류 발생: {str(e)}")  # 로그 기록 또는 추가 처리
            raise RuntimeError(f"PDF 생성 중 오류 발생: {str(e)}")

    def get_certificate_response(self):
        """
        PDF 파일을 HttpResponse로 반환하여 사용자가 다운로드할 수 있도록 합니다.
        """
        buffer = self.generate_certificate_pdf()
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="certificate_{self.certificate_id}.pdf"'
        )
        return response

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from django.conf import settings
from courses.models import MinorCategory, MajorCategory


def get_course_name(course_id, course_type):
    if course_type == "minor":
        try:
            return MinorCategory.objects.get(id=course_id).name
        except MinorCategory.DoesNotExist:
            raise ValueError("소분류 과정이 존재하지 않습니다.")
    elif course_type == "major":
        try:
            return MajorCategory.objects.get(id=course_id).name
        except MajorCategory.DoesNotExist:
            raise ValueError("대분류 과정이 존재하지 않습니다.")
    else:
        raise ValueError("유효하지 않은 과정 유형입니다.")


def load_image_and_fonts():
    image_path = os.path.join(
        settings.STATICFILES_DIRS[0], "img", "certificate_template.png"
    )
    font_path = os.path.join(
        settings.STATICFILES_DIRS[0], "fonts", "SongMyung-Regular.ttf"
    )

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"폰트 파일을 찾을 수 없습니다: {font_path}")

    image = Image.open(image_path)
    name_font = ImageFont.truetype(font_path, 90)
    course_font = ImageFont.truetype(font_path, 40)

    return image, name_font, course_font


def calculate_text_position(draw, text, font, image_width, y_position):
    text_width = draw.textbbox((0, 0), text, font=font)[2]
    position_x = (image_width - text_width) // 2
    return position_x, y_position


def draw_text(draw, text, position, font, color):
    draw.text(position, text, font=font, fill=color)


def generate_certificate(user_name, course_name):
    image, name_font, course_font = load_image_and_fonts()
    draw = ImageDraw.Draw(image)

    name_text_color = (191, 133, 46)
    course_text_color = (5, 5, 55)

    texts = [
        (user_name, name_font, name_text_color, 750),
        ("ORMCITY에서 제공하는", course_font, course_text_color, 950),
        (f"{course_name}을(를) 수료하였기에", course_font, course_text_color, 1050),
        ("이 증서를 드립니다.", course_font, course_text_color, 1150),
    ]

    for text, font, color, y_position in texts:
        position = calculate_text_position(draw, text, font, image.width, y_position)
        draw_text(draw, text, position, font, color)

    return image


def generate_certificate_image(user_name, course_name):
    image = generate_certificate(user_name, course_name)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def generate_certificate_pdf(user_name, course_name):
    image = generate_certificate(user_name, course_name)

    buffer = BytesIO()
    image.save(buffer, format="PDF")
    buffer.seek(0)

    return buffer

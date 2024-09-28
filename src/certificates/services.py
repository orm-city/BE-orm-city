import os
from io import BytesIO

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

from courses.models import MajorCategory, MinorCategory


def get_course_name(course_id, course_type):
    """
    주어진 코스 ID와 코스 유형에 따라 해당 코스의 이름을 반환합니다.

    Args:
        course_id (int): 코스의 ID.
        course_type (str): 코스의 유형 ('minor' 또는 'major').

    Returns:
        str: 코스의 이름.

    Raises:
        ValueError: 주어진 코스 ID에 해당하는 코스를 찾을 수 없거나, 유효하지 않은 코스 유형이 제공된 경우 발생합니다.
    """
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
    """
    인증서 생성에 필요한 이미지 템플릿과 폰트를 로드합니다.

    Returns:
        tuple: 이미지 객체, 이름 폰트, 코스 이름 폰트를 포함한 튜플.

    Raises:
        FileNotFoundError: 이미지 파일이나 폰트 파일을 찾을 수 없는 경우 발생합니다.
    """
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
    """
    주어진 텍스트를 이미지에 중앙 정렬하기 위한 X 위치를 계산합니다.

    Args:
        draw (ImageDraw): 이미지에 텍스트를 그리는 데 사용하는 ImageDraw 객체.
        text (str): 이미지에 그릴 텍스트.
        font (ImageFont): 텍스트에 사용할 폰트.
        image_width (int): 이미지의 너비.
        y_position (int): 텍스트의 Y 좌표.

    Returns:
        tuple: 텍스트의 X, Y 좌표를 포함한 튜플.
    """
    text_width = draw.textbbox((0, 0), text, font=font)[2]
    position_x = (image_width - text_width) // 2
    return position_x, y_position


def generate_certificate(user_name, course_name):
    """
    사용자 이름과 코스 이름을 포함한 인증서 이미지를 생성합니다.

    이 함수는 인증서 템플릿 이미지를 로드하고, 사용자 이름과 코스 관련 텍스트를 이미지 중앙에 배치하여 인증서 이미지를 생성합니다.

    Args:
        user_name (str): 인증서에 표시할 사용자 이름.
        course_name (str): 인증서에 표시할 코스 이름.

    Returns:
        Image: 생성된 인증서 이미지 객체.
    """
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
        draw.text(position, text, font=font, fill=color)

    return image


def generate_certificate_image(user_name, course_name):
    """
    사용자 이름과 코스 이름을 포함한 인증서 이미지를 생성하고, 이를 PNG 형식으로 반환합니다.

    Args:
        user_name (str): 인증서에 표시할 사용자 이름.
        course_name (str): 인증서에 표시할 코스 이름.

    Returns:
        BytesIO: 생성된 인증서 이미지의 PNG 버퍼.
    """
    image = generate_certificate(user_name, course_name)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def generate_certificate_pdf(user_name, course_name):
    """
    사용자 이름과 코스 이름을 포함한 인증서 이미지를 생성하고, 이를 PDF 형식으로 반환합니다.

    Args:
        user_name (str): 인증서에 표시할 사용자 이름.
        course_name (str): 인증서에 표시할 코스 이름.

    Returns:
        BytesIO: 생성된 인증서 이미지의 PDF 버퍼.
    """
    image = generate_certificate(user_name, course_name)

    buffer = BytesIO()
    image.save(buffer, format="PDF")
    buffer.seek(0)

    return buffer

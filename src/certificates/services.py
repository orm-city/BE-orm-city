import os
from base64 import b64encode, b64decode
from io import BytesIO

import qrcode

from django.conf import settings
from django.db.models import Count, Q, F
from django.contrib.contenttypes.models import ContentType

from PIL import Image, ImageDraw, ImageFont
from Crypto.Cipher import AES

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


def generate_certificate(user_name, course_name, certificate_id=None):
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

    qr_buffer = generate_certificate_qr(certificate_id)
    qr_image = Image.open(qr_buffer)

    # QR 코드 위치 설정 (하단 오른쪽 구석)
    qr_position = (
        image.width - qr_image.width - 50,
        image.height - qr_image.height - 50,
    )
    image.paste(qr_image, qr_position)

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


def generate_certificate_pdf(user_name, course_name, certificate_id):
    """
    사용자 이름과 코스 이름을 포함한 인증서 이미지를 생성하고, 이를 PDF 형식으로 반환합니다.

    Args:
        user_name (str): 인증서에 표시할 사용자 이름.
        course_name (str): 인증서에 표시할 코스 이름.
        certificate_id (str): 인증서 ID.

    Returns:
        BytesIO: 생성된 인증서 이미지의 PDF 버퍼.
    """
    image = generate_certificate(user_name, course_name, certificate_id)

    buffer = BytesIO()
    image.save(buffer, format="PDF")
    buffer.seek(0)

    return buffer


def generate_certificate_qr(certificate_id):
    """
    주어진 인증서 ID를 포함한 QR 코드를 생성하여 반환합니다.

    Args:
        certificate_id (str): 인증서 ID.

    Returns:
        BytesIO: 생성된 QR 코드 이미지의 PNG 버퍼.
    """
    frontend_host = getattr(settings, "FRONTEND_HOST", "http://localhost:5500")
    qr_data = (
        f"{frontend_host}/certificate_verification.html?certificate_id={certificate_id}"
    )
    qr = qrcode.make(qr_data)

    # QR 코드를 메모리 내 이미지로 저장
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def get_course_model(course_type):
    """
    주어진 코스 유형에 따라 해당 코스 모델을 반환합니다.

    Args:
        course_type (str): 코스 유형 ('minor' 또는 'major').

    Returns:
        Model: 해당 코스 모델.

    Raises:
        ValueError: 유효하지 않은 코스 유형이 제공된 경우 발생합니다.
    """
    if course_type == "minor":
        return MinorCategory
    elif course_type == "major":
        return MajorCategory
    else:
        raise ValueError("유효하지 않은 과정 유형입니다.")


######################################################################
## permissions.py
def get_available_certificates(user):
    """
    사용자가 MinorCategory 또는 MajorCategory의 모든 동영상을 완료했는지 확인하여
    발급 가능한 수료증 목록을 반환합니다.

    Args:
        user (User): 인증서를 요청한 사용자.

    Returns:
        tuple: 발급 가능한 MinorCategory와 MajorCategory 수료증 목록을 포함한 튜플.
    """
    # MinorCategory의 모든 동영상을 완료한 경우 발급 가능 목록
    available_minor_certificates = MinorCategory.objects.annotate(
        total_videos=Count("videos"),
        completed_videos=Count(
            "videos",
            filter=Q(
                videos__progresses__user=user, videos__progresses__is_completed=True
            ),
        ),
    ).filter(total_videos=F("completed_videos"))

    # MajorCategory의 모든 동영상을 완료한 경우 발급 가능 목록
    available_major_certificates = MajorCategory.objects.annotate(
        total_videos=Count("minor_categories__videos"),
        completed_videos=Count(
            "minor_categories__videos",
            filter=Q(
                minor_categories__videos__progresses__user=user,
                minor_categories__videos__progresses__is_completed=True,
            ),
        ),
    ).filter(total_videos=F("completed_videos"))

    return available_minor_certificates, available_major_certificates


######################################################################
## 암호화, 복호화
def encrypt_certificate_data(data):
    """
    주어진 데이터를 AES 암호화하여 반환합니다.

    Args:
        data (str): 암호화할 데이터.

    Returns:
        str: 암호화된 데이터 (Base64로 인코딩).

    Raises:
        ValueError: 암호화 중 오류가 발생한 경우.
    """
    key = settings.CERTIFICATE_SECRET_KEY.encode("utf-8")
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode("utf-8"))

    # Nonce, tag, ciphertext를 결합하여 저장
    encrypted_data = b64encode(cipher.nonce + tag + ciphertext).decode("utf-8")
    return encrypted_data


def decrypt_certificate_data(encrypted_data):
    """
    주어진 암호화된 데이터를 복호화하여 원본 데이터를 반환합니다.

    Args:
        encrypted_data (str): 복호화할 암호화된 데이터 (Base64로 인코딩된 문자열).

    Returns:
        str: 복호화된 원본 데이터.

    Raises:
        ValueError: 복호화 중 오류가 발생한 경우.
    """
    key = settings.CERTIFICATE_SECRET_KEY.encode("utf-8")
    encrypted_data = b64decode(encrypted_data)

    # Nonce, tag, ciphertext 분리
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]

    # 복호화 시 Nonce 전달
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    # 복호화 진행 및 검증
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return data.decode("utf-8")

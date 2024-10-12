import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from certificates.services import encrypt_certificate_data


class Certificate(models.Model):
    """
    수료증 모델: 사용자가 특정 과정을 완료했을 때 발행되는 수료증 정보를 저장합니다.
    
    Attributes:
        user (ForeignKey): 수료증을 발급받은 사용자.
        content_type (ForeignKey): 수료증이 발급된 과정의 콘텐츠 타입.
        object_id (PositiveIntegerField): 해당 콘텐츠 객체의 ID.
        course (GenericForeignKey): 콘텐츠 타입과 객체 ID로 연결된 과정.
        issued_at (DateTimeField): 수료증 발급일.
        certificate_id (UUIDField): 수료증의 고유 ID.
        encrypted_data (TextField): 암호화된 수료증 데이터.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="사용자",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="콘텐츠 타입",
    )
    object_id = models.PositiveIntegerField(verbose_name="객체 ID")
    course = GenericForeignKey("content_type", "object_id")
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="발급일")
    certificate_id = models.UUIDField(
        default=uuid.uuid4, unique=True, verbose_name="수료증 ID"
    )
    encrypted_data = models.TextField(verbose_name="암호화된 데이터")

    class Meta:
        verbose_name = "수료증"
        verbose_name_plural = "수료증들"

    def generate_certificate(self):
        """
        수료증 데이터를 생성하고, 암호화하여 encrypted_data 필드에 저장합니다.
        
        수료증에는 사용자 이름, 과정 이름, 발급일 등의 정보가 포함되며,
        해당 정보를 암호화하여 데이터베이스에 저장합니다.
        """
        data = f"User: {self.user.username}, Course: {self.course.name}, Issued At: {self.issued_at}"

        # 암호화된 데이터를 encrypted_data 필드에 저장
        self.encrypted_data = encrypt_certificate_data(data)

        # 수료증 데이터를 데이터베이스에 저장
        self.save()

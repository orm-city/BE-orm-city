import uuid

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from accounts.models import CustomUser as User
from certificates.services import encrypt_certificate_data


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    course = GenericForeignKey("content_type", "object_id")
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.UUIDField(default=uuid.uuid4, unique=True)
    encrypted_data = models.TextField()  # 암호화된 수료증 데이터

    def generate_certificate(self):
        # 수료증 데이터 생성
        data = f"User: {self.user.username}, Course: {self.course.name}, Issued At: {self.issued_at}"
        print(f"Data to Encrypt: {data}")

        # 암호화된 데이터를 encrypted_data 필드에 저장
        self.encrypted_data = encrypt_certificate_data(data)
        print(f"Encrypted Data Before Saving: {self.encrypted_data}")
        self.save()

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ["user", "course", "issued_at", "certificate_id"]

    def get_course(self, obj):
        return obj.course.name  # course 이름 반환

    def create(self, validated_data):
        user = validated_data["user"]
        course = self.context["course"]  # course를 context에서 받아옴

        # MajorCategory 또는 MinorCategory인지 확인
        course_content_type = ContentType.objects.get_for_model(course)

        # Certificate 객체 생성
        certificate = Certificate.objects.create(
            user=user,
            content_type=course_content_type,
            object_id=course.id,
        )
        certificate.generate_certificate()  # 수료증 데이터 암호화 및 저장
        return certificate

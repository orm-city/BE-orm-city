from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType

from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    """
    수료증(Certificate) 모델을 위한 직렬화기.
    
    사용자와 과정, 발급일, 수료증 ID를 직렬화하며, 과정(course) 이름을 반환하는 커스텀 필드를 포함합니다.
    """
    
    course = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ["user", "course", "issued_at", "certificate_id"]

    def get_course(self, obj):
        """
        과정 이름을 반환하는 메서드.
        
        Args:
            obj (Certificate): 수료증 객체.
        
        Returns:
            str: 과정의 이름.
        """
        return obj.course.name  # course 이름 반환

    def create(self, validated_data):
        """
        수료증을 생성하고 저장하는 메서드.
        
        과정이 MajorCategory 또는 MinorCategory에 속하는지 확인하고,
        주어진 사용자와 과정을 기반으로 수료증을 생성합니다.
        
        Args:
            validated_data (dict): 유효성 검증을 마친 데이터.
        
        Returns:
            Certificate: 생성된 수료증 객체.
        """
        user = validated_data["user"]
        course = self.context["course"]  # course를 context에서 받아옴

        # MajorCategory 또는 MinorCategory인지 확인하고 ContentType 가져옴
        course_content_type = ContentType.objects.get_for_model(course)

        # Certificate 객체 생성
        certificate = Certificate.objects.create(
            user=user,
            content_type=course_content_type,
            object_id=course.id,
        )
        certificate.generate_certificate()  # 수료증 데이터 암호화 및 저장
        return certificate

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, UserActivity


class CustomUserSerializer(serializers.ModelSerializer):
    """CustomUser 모델을 위한 시리얼라이저.

    이 시리얼라이저는 사용자 생성, 수정, 조회를 위한 필드들을 정의합니다.
    비밀번호 유효성 검사와 확인 과정을 포함합니다.

    Attributes:
        password (CharField): 사용자 비밀번호. 쓰기 전용이며 Django의 기본 비밀번호 검증을 사용합니다.
        password2 (CharField): 비밀번호 확인 필드. 쓰기 전용입니다.
        is_subscription_active (BooleanField): 사용자의 구독 활성 상태. 읽기 전용입니다.
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    is_subscription_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "role",
            "nickname",
            "total_study_time",
            "subscription_end_date",
            "gender",
            "contact_number",
            "is_subscription_active",
        ]
        read_only_fields = ["id", "total_study_time", "subscription_end_date"]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        """입력된 데이터의 유효성을 검사합니다.
        비밀번호와 비밀번호 확인 필드가 일치하는지 확인합니다.

        Args:
            attrs (dict): 유효성을 검사할 데이터 딕셔너리.

        Returns:
            dict: 유효성이 확인된 데이터 딕셔너리.

        Raises:
            serializers.ValidationError: 비밀번호가 일치하지 않을 경우 발생합니다.
        """
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """새로운 CustomUser 인스턴스를 생성합니다.
        Args:
            validated_data (dict): 유효성이 검증된 데이터 딕셔너리.

        Returns:
            CustomUser: 새로 생성된 CustomUser 인스턴스.
        """
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """기존 CustomUser 인스턴스를 업데이트합니다.
        비밀번호가 제공된 경우, 이를 별도로 처리합니다.

        Args:
            instance (CustomUser): 업데이트할 CustomUser 인스턴스.
            validated_data (dict): 유효성이 검증된 업데이트 데이터.

        Returns:
            CustomUser: 업데이트된 CustomUser 인스턴스.
        """
        if "password" in validated_data:
            password = validated_data.pop("password")
            validated_data.pop("password2", None)
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserActivitySerializer(serializers.ModelSerializer):
    """UserActivity 모델을 위한 시리얼라이저.

    사용자의 로그인/로그아웃 활동을 기록하고 조회하는 데 사용됩니다.

    Attributes:
        user (StringRelatedField): 활동과 관련된 사용자. 문자열로 표현됩니다.
    """

    user = serializers.StringRelatedField()

    class Meta:
        model = UserActivity
        fields = ["id", "user", "login_time", "logout_time", "ip_address"]
        read_only_fields = ["id", "user", "login_time", "ip_address"]

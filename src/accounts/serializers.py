from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, UserActivity


class UserSerializer(serializers.ModelSerializer):
    """
    CustomUser 모델의 필드 정보를 직렬화하는 Serializer.

    Meta 클래스:
        model (CustomUser): 직렬화할 모델.
        fields (list): 포함할 필드 목록 ['id', 'email', 'username', 'role', 'nickname'].
        read_only_fields (list): 읽기 전용 필드 목록 ['email', 'role'].
    """

    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "role", "nickname"]
        read_only_fields = ["email", "role"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    사용자 등록을 위한 Serializer.

    필드:
        password (CharField): 비밀번호 필드. 쓰기 전용.

    Meta 클래스:
        model (CustomUser): 직렬화할 모델.
        fields (list): 포함할 필드 목록 ['email', 'username', 'password', 'nickname'].
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password", "nickname"]

    def create(self, validated_data):
        """
        유효성 검사를 통과한 데이터를 사용하여 새 사용자를 생성합니다.

        Args:
            validated_data (dict): 유효성 검사를 통과한 데이터.

        Returns:
            CustomUser: 생성된 사용자 객체.
        """
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname", ""),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    사용자 로그인을 처리하기 위한 Serializer.

    필드:
        email (EmailField): 사용자의 이메일.
        password (CharField): 사용자의 비밀번호.
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """
        제공된 자격 증명을 사용해 사용자를 인증합니다.

        Args:
            data (dict): 사용자 이메일과 비밀번호.

        Returns:
            CustomUser: 인증된 사용자 객체.

        Raises:
            serializers.ValidationError: 자격 증명이 잘못된 경우 발생.
        """
        user = authenticate(email=data["email"], password=data["password"])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class UserActivitySerializer(serializers.ModelSerializer):
    """
    사용자 활동 정보를 직렬화하는 Serializer.

    Meta 클래스:
        model (UserActivity): 직렬화할 모델.
        fields (list): 포함할 필드 목록 ['login_time', 'logout_time'].
    """

    class Meta:
        model = UserActivity
        fields = ["login_time", "logout_time"]


class ManagerCreationSerializer(serializers.ModelSerializer):
    """
    관리자 사용자를 생성하기 위한 Serializer.

    필드:
        password (CharField): 비밀번호 필드. 쓰기 전용.

    Meta 클래스:
        model (CustomUser): 직렬화할 모델.
        fields (list): 포함할 필드 목록 ['email', 'username', 'password', 'nickname'].
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password", "nickname"]

    def create(self, validated_data):
        """
        유효성 검사를 통과한 데이터를 사용해 관리자 사용자를 생성합니다.

        Args:
            validated_data (dict): 유효성 검사를 통과한 데이터.

        Returns:
            CustomUser: 생성된 관리자 사용자 객체.
        """
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname", ""),
            role="manager",
        )
        return user

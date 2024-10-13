from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, UserActivity


class UserSerializer(serializers.ModelSerializer):
    """
    CustomUser 모델을 위한 직렬화 클래스.

    이 클래스는 사용자 정보를 직렬화 및 역직렬화하며, 이메일과 역할 필드는 읽기 전용으로 설정되어 있습니다.

    속성:
        model (CustomUser): 직렬화할 모델.
        fields (list): 직렬화할 필드 목록.
        read_only_fields (list): 읽기 전용 필드 목록.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "role", "nickname"]
        read_only_fields = ["email", "role"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    사용자 등록을 처리하는 직렬화 클래스.

    비밀번호는 write_only로 설정되며, 사용자 등록 후 JWT 토큰을 반환합니다.

    메서드:
        get_tokens: 사용자에 대한 액세스 및 리프레시 토큰을 생성합니다.
        create: 새로운 사용자를 생성합니다.
    """

    password = serializers.CharField(write_only=True)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password", "nickname", "tokens"]

    def get_tokens(self, user):
        """
        주어진 사용자에 대한 액세스 및 리프레시 토큰을 반환합니다.

        Args:
            user (CustomUser): 토큰을 생성할 사용자.

        Returns:
            dict: 리프레시 및 액세스 토큰.
        """
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def create(self, validated_data):
        """
        사용자 데이터를 이용해 새 사용자를 생성합니다.

        Args:
            validated_data (dict): 검증된 사용자 데이터.

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
    사용자 로그인을 처리하는 직렬화 클래스.

    사용자가 인증되면 JWT 토큰을 반환합니다.

    메서드:
        validate: 사용자의 이메일과 비밀번호를 검증하고 토큰을 반환합니다.
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """
        주어진 이메일과 비밀번호로 사용자를 인증하고, JWT 토큰을 반환합니다.

        Args:
            data (dict): 사용자의 이메일과 비밀번호.

        Returns:
            dict: 인증된 사용자 및 토큰.

        Raises:
            serializers.ValidationError: 이메일 또는 비밀번호가 올바르지 않을 경우.
        """
        user = authenticate(email=data["email"], password=data["password"])
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return {
                "user": user,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        raise serializers.ValidationError("Incorrect Credentials")


class UserActivitySerializer(serializers.ModelSerializer):
    """
    사용자의 활동 기록을 직렬화하는 클래스.

    속성:
        model (UserActivity): 직렬화할 모델.
        fields (list): 직렬화할 필드 목록.
    """

    class Meta:
        model = UserActivity
        fields = ["login_time", "logout_time"]


class ManagerCreationSerializer(serializers.ModelSerializer):
    """
    매니저 사용자를 생성하는 직렬화 클래스.

    메서드:
        get_tokens: 매니저에 대한 액세스 및 리프레시 토큰을 생성합니다.
        create: 새로운 매니저 사용자를 생성합니다.
    """

    password = serializers.CharField(write_only=True)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password", "nickname", "tokens"]

    def get_tokens(self, user):
        """
        주어진 매니저 사용자에 대한 액세스 및 리프레시 토큰을 반환합니다.

        Args:
            user (CustomUser): 토큰을 생성할 사용자.

        Returns:
            dict: 리프레시 및 액세스 토큰.
        """
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def create(self, validated_data):
        """
        사용자 데이터를 이용해 새 매니저 사용자를 생성합니다.

        Args:
            validated_data (dict): 검증된 사용자 데이터.

        Returns:
            CustomUser: 생성된 매니저 사용자 객체.
        """
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname", ""),
            role="manager",
        )
        return user

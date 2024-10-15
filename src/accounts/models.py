from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    사용자 생성을 담당하는 커스텀 매니저 클래스.

    메서드:
        create_user: 일반 사용자를 생성하는 메서드.
        create_superuser: 관리자 사용자를 생성하는 메서드.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """
        이메일, 사용자 이름, 비밀번호를 이용해 일반 사용자를 생성합니다.

        Args:
            email (str): 사용자의 이메일.
            username (str): 사용자의 이름.
            password (str, optional): 사용자의 비밀번호. 기본값은 None.
            **extra_fields: 추가 필드 (예: role).

        Returns:
            CustomUser: 생성된 사용자 객체.

        Raises:
            ValueError: 이메일 필드가 설정되지 않았을 때 발생.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", "student")
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        이메일, 사용자 이름, 비밀번호를 이용해 관리자 사용자를 생성합니다.

        Args:
            email (str): 관리자의 이메일.
            username (str): 관리자의 사용자 이름.
            password (str, optional): 관리자의 비밀번호. 기본값은 None.
            **extra_fields: 추가 필드 (예: role, is_staff, is_superuser).

        Returns:
            CustomUser: 생성된 관리자 사용자 객체.

        Raises:
            ValueError: is_staff 또는 is_superuser가 True가 아닌 경우.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    사용자 모델을 확장한 커스텀 사용자 클래스.

    속성:
        email (EmailField): 사용자의 이메일 (고유 필드).
        role (CharField): 사용자의 역할 (학생, 관리자 또는 어드민).
        nickname (CharField): 사용자의 닉네임 (옵션 필드).
    """

    ROLE_CHOICES = [
        ("student", "학생"),
        ("manager", "관리자"),
        ("admin", "어드민"),
    ]

    email = models.EmailField(unique=True, verbose_name="이메일")
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default="student", verbose_name="역할"
    )
    nickname = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="닉네임"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        """
        사용자 객체의 문자열 표현을 반환합니다.

        Returns:
            str: 사용자 이름과 역할의 문자열.
        """
        return f"{self.username} ({self.get_role_display()})"


class UserActivity(models.Model):
    """
    사용자의 활동(로그인 및 로그아웃 시간)을 기록하는 모델.

    속성:
        user (ForeignKey): 관련된 사용자 객체.
        login_time (DateTimeField): 사용자의 로그인 시간.
        logout_time (DateTimeField): 사용자의 로그아웃 시간.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="로그인 시간")
    logout_time = models.DateTimeField(
        null=True, blank=True, verbose_name="로그아웃 시간"
    )

    class Meta:
        verbose_name = "사용자 활동"
        verbose_name_plural = "사용자 활동 목록"

    def __str__(self):
        """
        사용자 활동 객체의 문자열 표현을 반환합니다.

        Returns:
            str: 사용자 이름과 로그인 시간의 문자열.
        """
        return f"{self.user.username}의 활동 - 로그인: {self.login_time}"

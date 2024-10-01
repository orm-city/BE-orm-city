from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from .models import CustomUser, UserActivity
from .serializers import CustomUserSerializer, UserActivitySerializer


class RegisterView(generics.CreateAPIView):
    """
    사용자 등록을 처리하는 뷰.

    이 뷰는 새로운 사용자 계정을 생성하고, 사용자의 첫 활동을 기록합니다.

    Attributes:
        queryset: 모든 CustomUser 객체.
        serializer_class: 사용자 데이터를 직렬화/역직렬화하는 데 사용되는 시리얼라이저.
        permission_classes: 이 뷰에 접근할 수 있는 권한(모든 사용자 허용).
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        사용자 생성을 수행하고 첫 활동을 기록합니다.

        Args:
            serializer: 유효성이 검증된 사용자 데이터를 포함한 시리얼라이저.

        Returns:
            None
        """
        user = serializer.save()
        UserActivity.objects.create(
            user=user, ip_address=self.request.META.get("REMOTE_ADDR", None)
        )


class LoginView(APIView):
    """
    사용자 로그인을 처리하는 뷰.

    이 뷰는 사용자 인증을 수행하고, 성공 시 JWT 토큰을 발급합니다.

    Attributes:
        permission_classes: 이 뷰에 접근할 수 있는 권한(모든 사용자 허용).
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST 요청을 처리하여 사용자 로그인을 수행합니다.

        Args:
            request: 클라이언트로부터의 HTTP 요청 객체.

        Returns:
            Response: JWT 토큰을 포함한 응답 또는 오류 메시지.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        user = CustomUser.objects.filter(username=username).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            UserActivity.objects.create(
                user=user, ip_address=request.META.get("REMOTE_ADDR", None)
            )
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """
    사용자 로그아웃을 처리하는 API 뷰.

    이 뷰는 사용자의 리프레시 토큰을 블랙리스트에 추가하고,
    해당 사용자의 가장 최근 UserActivity 기록의 로그아웃 시간을 업데이트합니다.

    Attributes:
        permission_classes (list): 이 뷰에 접근할 수 있는 권한을 정의합니다.
                                   [IsAuthenticated]로 설정되어 인증된 사용자만 접근 가능합니다.

    Methods:
        post(request): POST 요청을 처리하여 사용자 로그아웃을 수행합니다.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST 요청을 처리하여 사용자 로그아웃을 수행합니다.

        이 메서드는 다음과 같은 작업을 수행합니다:
        1. 요청에서 리프레시 토큰을 추출합니다.
        2. 해당 토큰을 블랙리스트에 추가합니다.
        3. 사용자의 가장 최근 UserActivity 기록을 찾아 로그아웃 시간을 업데이트합니다.

        Args:
            request (Request): 클라이언트로부터의 HTTP 요청 객체.
                               이 요청의 데이터에는 'refresh' 키로 리프레시 토큰이 포함되어야 합니다.

        Returns:
            Response: 로그아웃 처리 결과를 나타내는 HTTP 응답.
                      - 성공 시: 205 상태 코드와 성공 메시지를 반환합니다.
                      - 실패 시: 400 또는 500 상태 코드와 오류 메시지를 반환합니다.

        Raises:
            KeyError: 'refresh' 키가 요청 데이터에 없을 경우 발생합니다.
            TokenError: 제공된 토큰이 유효하지 않거나 이미 블랙리스트에 있는 경우 발생합니다.
            Exception: 예상치 못한 오류가 발생할 경우 처리합니다.

        Note:
            - 이 메서드는 djangorestframework-simplejwt의 RefreshToken을 사용하여 토큰을 처리합니다.
            - UserActivity 모델을 사용하여 사용자의 로그아웃 시간을 기록합니다.
            - 모든 예외는 적절한 HTTP 응답으로 처리되어 클라이언트에게 반환됩니다.
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            user_activity = (
                UserActivity.objects.filter(user=request.user, logout_time__isnull=True)
                .order_by("-login_time")
                .first()
            )

            if user_activity:
                user_activity.logout_time = timezone.now()
                user_activity.save()

            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except KeyError:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    사용자 프로필 조회 및 수정을 처리하는 뷰.

    이 뷰는 인증된 사용자의 프로필 정보를 조회하고 수정할 수 있게 합니다.

    Attributes:
        serializer_class: 사용자 데이터를 직렬화/역직렬화하는 데 사용되는 시리얼라이저.
        permission_classes: 이 뷰에 접근할 수 있는 권한(인증된 사용자만 허용).
    """

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        현재 인증된 사용자 객체를 반환합니다.

        Returns:
            CustomUser: 현재 인증된 사용자 객체.
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        PUT 또는 PATCH 요청을 처리하여 사용자 프로필을 업데이트합니다.

        Args:
            request: 클라이언트로부터의 HTTP 요청 객체.
            *args: 추가 위치 인자.
            **kwargs: 추가 키워드 인자.

        Returns:
            Response: 업데이트된 사용자 데이터를 포함한 응답.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class UserActivityListView(generics.ListAPIView):
    """
    사용자 활동 내역을 조회하는 뷰.

    이 뷰는 인증된 사용자의 모든 활동 내역을 반환합니다.

    Attributes:
        serializer_class: 사용자 활동 데이터를 직렬화하는 데 사용되는 시리얼라이저.
        permission_classes: 이 뷰에 접근할 수 있는 권한(인증된 사용자만 허용).
    """

    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        현재 인증된 사용자의 활동 내역을 반환합니다.

        Returns:
            QuerySet: 현재 사용자의 UserActivity 객체 쿼리셋.
        """
        return UserActivity.objects.filter(user=self.request.user)


class DeleteAccountView(APIView):
    """
    사용자 계정 삭제(비활성화)를 처리하는 뷰.

    이 뷰는 인증된 사용자의 계정을 비활성화합니다.

    Attributes:
        permission_classes: 이 뷰에 접근할 수 있는 권한(인증된 사용자만 허용).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST 요청을 처리하여 사용자 계정을 비활성화합니다.

        Args:
            request: 클라이언트로부터의 HTTP 요청 객체.

        Returns:
            Response: 성공 또는 실패 메시지를 포함한 응답.
        """
        user = request.user
        password = request.data.get("password")

        if user.check_password(password):
            user.is_active = False
            user.save()
            return Response(
                {"message": "계정이 비활성화되었습니다."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "비밀번호가 올바르지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

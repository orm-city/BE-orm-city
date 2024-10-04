from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from .models import CustomUser, UserActivity
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserActivitySerializer,
    ManagerCreationSerializer,
)
from .permissions import IsAdminUser, IsManagerOrAdminUser


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    사용자 관리 기능을 제공하는 ViewSet.

    - 관리자(admin)는 모든 사용자에 접근할 수 있습니다.
    - 관리자(manager)는 학생 계정만 관리할 수 있습니다.

    속성:
        queryset (QuerySet): 사용자 목록.
        serializer_class (UserSerializer): 직렬화할 클래스.
        permission_classes (list): 접근 권한을 설정하는 클래스.

    메서드:
        get_queryset(): 요청자의 역할에 따라 사용자 목록을 반환합니다.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdminUser]

    def get_queryset(self):
        """
        요청자의 역할에 따라 사용자 목록을 필터링합니다.

        Returns:
            QuerySet: 필터링된 사용자 목록.
        """
        if self.request.user.role == "admin":
            return CustomUser.objects.all()
        elif self.request.user.role == "manager":
            return CustomUser.objects.filter(role="student")
        return CustomUser.objects.filter(id=self.request.user.id)


class RegisterView(generics.CreateAPIView):
    """
    사용자 등록을 처리하는 뷰.

    - 누구나 접근 가능합니다.

    속성:
        queryset (QuerySet): 사용자 목록.
        serializer_class (UserRegistrationSerializer): 직렬화할 클래스.
        permission_classes (list): 접근 권한을 설정하는 클래스.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    """
    사용자 로그인을 처리하는 뷰.

    - 누구나 접근 가능합니다.

    메서드:
        post(request): 사용자의 자격 증명을 확인하고 로그인 처리합니다.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        사용자의 자격 증명을 확인하고 로그인 처리합니다.

        Args:
            request (Request): 사용자의 요청 데이터.

        Returns:
            Response: 로그인 성공 시 사용자 정보, 실패 시 오류 메시지.
        """
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    """
    사용자 로그아웃을 처리하는 뷰.

    - 인증된 사용자만 접근 가능합니다.

    메서드:
        post(request): 사용자를 로그아웃 처리합니다.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        요청한 사용자를 로그아웃 처리합니다.

        Args:
            request (Request): 사용자의 요청 데이터.

        Returns:
            Response: 로그아웃 성공 메시지.
        """
        logout(request)
        return Response({"detail": "Successfully logged out."})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    인증된 사용자의 프로필 정보를 조회 및 업데이트하는 뷰.

    - 인증된 사용자만 접근 가능합니다.

    속성:
        serializer_class (UserSerializer): 직렬화할 클래스.
        permission_classes (list): 접근 권한을 설정하는 클래스.

    메서드:
        get_object(): 요청한 사용자 객체를 반환합니다.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        현재 요청한 사용자의 프로필 객체를 반환합니다.

        Returns:
            CustomUser: 현재 사용자 객체.
        """
        return self.request.user


class UserActivityListView(generics.ListAPIView):
    """
    인증된 사용자의 활동 로그 목록을 조회하는 뷰.

    - 인증된 사용자만 접근 가능합니다.

    속성:
        serializer_class (UserActivitySerializer): 직렬화할 클래스.
        permission_classes (list): 접근 권한을 설정하는 클래스.

    메서드:
        get_queryset(): 현재 사용자의 활동 로그를 반환합니다.
    """

    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        현재 사용자의 활동 로그를 반환합니다.

        Returns:
            QuerySet: 현재 사용자의 활동 목록.
        """
        return UserActivity.objects.filter(user=self.request.user)


class DeleteAccountView(APIView):
    """
    인증된 사용자의 계정을 삭제하는 뷰.

    - 인증된 사용자만 접근 가능합니다.

    메서드:
        delete(request): 현재 사용자의 계정을 삭제합니다.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """
        요청한 사용자의 계정을 삭제합니다.

        Args:
            request (Request): 사용자의 요청 데이터.

        Returns:
            Response: 계정 삭제 성공 메시지.
        """
        user = request.user
        user.delete()
        return Response(
            {"detail": "Account successfully deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ManagerCreationView(APIView):
    """
    관리자 계정을 생성하는 뷰.

    - 관리자(admin)만 접근 가능합니다.

    메서드:
        post(request): 새로운 관리자 계정을 생성합니다.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        """
        새로운 관리자 계정을 생성합니다.

        Args:
            request (Request): 사용자의 요청 데이터.

        Returns:
            Response: 관리자 계정 생성 성공 메시지.
        """
        serializer = ManagerCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Manager user created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserRoleView(APIView):
    """
    사용자의 역할을 변경하는 뷰.

    - 관리자(admin)만 접근 가능합니다.

    메서드:
        patch(request, user_id): 특정 사용자의 역할을 변경합니다.
    """

    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        """
        사용자의 역할을 변경합니다.

        Args:
            request (Request): 사용자의 요청 데이터.
            user_id (int): 역할을 변경할 사용자의 ID.

        Returns:
            Response: 업데이트된 사용자 정보 또는 오류 메시지.
        """
        try:
            user = CustomUser.objects.get(id=user_id)
            new_role = request.data.get("role")
            if new_role not in ["student", "manager"]:
                return Response(
                    {"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST
                )
            user.role = new_role
            user.save()
            return Response(UserSerializer(user).data)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

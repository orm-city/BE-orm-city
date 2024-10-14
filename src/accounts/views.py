from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import CustomUser, UserActivity
from .schema import (
    paginated_response_schema, 
    user_list_schema, 
    user_retrieve_schema, 
    user_create_schema, 
    user_update_schema, 
    user_partial_update_schema, 
    user_destroy_schema, 
    register_view_schema, 
    login_view_schema, 
    logout_view_schema, 
    user_profile_retrieve_schema, 
    user_profile_update_schema, 
    user_activity_list_schema, 
    delete_account_schema, 
    manager_creation_schema, 
    change_user_role_schema, 
    role_check_schema
    )
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserActivitySerializer,
    ManagerCreationSerializer,
)
from .permissions import IsManagerOrAdminUser, IsAdminUser


class StandardResultsSetPagination(PageNumberPagination):
    """
    페이지네이션 설정 클래스.
    
    기본적으로 페이지당 10개의 결과를 반환하며, 요청에 따라 페이지 크기를 조정할 수 있습니다.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

@paginated_response_schema
def some_view(request):
    # API 로직 처리
    pass


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    사용자 관리를 위한 ViewSet입니다.
    
    관리자는 모든 사용자에 접근할 수 있으며, 매니저는 학생만 볼 수 있습니다.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @user_list_schema
    def list(self, request):
        return super().list(request)

    @user_retrieve_schema
    def retrieve(self, request, pk=None):
        return super().retrieve(request, pk)

    @user_create_schema
    def create(self, request):
        return super().create(request)

    @user_update_schema
    def update(self, request, pk=None):
        return super().update(request, pk)

    @user_partial_update_schema
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)

    @user_destroy_schema
    def destroy(self, request, pk=None):
        return super().destroy(request, pk)
    

    def get_queryset(self):
        """
        요청자의 역할에 따라 사용자 목록을 필터링합니다.
        
        Returns:
            QuerySet: 필터링된 사용자 목록.
        """
        user = self.request.user
        if user.role == "admin":
            return CustomUser.objects.all()
        elif user.role == "manager":
            return CustomUser.objects.filter(role="student")
        else:
            return CustomUser.objects.filter(id=user.id)

    def get_permissions(self):
        """
        요청하는 액션에 따라 권한을 설정합니다.
        
        Returns:
            list: 해당 요청에 대한 권한 클래스 목록.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminUser]
        elif self.action == "list":
            self.permission_classes = [IsManagerOrAdminUser]
        elif self.action == "retrieve":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class RegisterView(generics.CreateAPIView):
    """
    새로운 사용자를 등록하는 뷰입니다.
    
    등록 성공 시 사용자 정보와 함께 액세스 토큰과 리프레시 토큰을 반환합니다.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @register_view_schema  # 스키마 적용
    def create(self, request, *args, **kwargs):
        """
        사용자를 등록하고, 사용자 정보와 토큰을 반환합니다.
        
        Args:
            request (Request): 사용자 등록 요청 데이터.

        Returns:
            Response: 사용자 정보 및 액세스, 리프레시 토큰.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    사용자 로그인을 처리하는 뷰입니다.
    
    로그인 성공 시 사용자 정보와 함께 액세스 토큰과 리프레시 토큰을 반환합니다.
    """
    permission_classes = [AllowAny]

    @login_view_schema 
    def post(self, request):
        """
        사용자의 로그인 요청을 처리합니다.
        
        Args:
            request (Request): 로그인 요청 데이터.

        Returns:
            Response: 사용자 정보 및 액세스, 리프레시 토큰.
        """
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    사용자 로그아웃을 처리하는 뷰입니다.
    
    로그아웃 성공 시 리프레시 토큰을 블랙리스트에 추가합니다.
    """
    permission_classes = [IsAuthenticated]

    @logout_view_schema
    def post(self, request):
        """
        사용자의 로그아웃 요청을 처리하고, 리프레시 토큰을 블랙리스트에 추가합니다.
        
        Args:
            request (Request): 로그아웃 요청 데이터.

        Returns:
            Response: 로그아웃 성공 메시지.
        """
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    현재 로그인한 사용자의 프로필 정보를 조회하거나 수정하는 뷰입니다.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @user_profile_retrieve_schema  
    def retrieve(self, request, *args, **kwargs):
        """
        현재 사용자의 프로필 정보를 조회합니다.
        """
        return super().retrieve(request, *args, **kwargs)

    @user_profile_update_schema  
    def update(self, request, *args, **kwargs):
        """
        현재 사용자의 프로필 정보를 수정합니다.
        """
        return super().update(request, *args, **kwargs)
    
    def get_object(self):
        """
        현재 로그인한 사용자 객체를 반환합니다.
        
        Returns:
            User: 현재 요청의 사용자 객체.
        """
        return self.request.user


class UserActivityListView(generics.ListAPIView):
    """
    현재 로그인한 사용자의 활동 기록을 조회하는 뷰입니다.
    """
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    @user_activity_list_schema  # 스키마 분리 적용
    def get(self, request, *args, **kwargs):
        """
        현재 사용자의 활동 기록을 조회합니다.
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        현재 로그인한 사용자의 활동 기록을 반환합니다.
        
        Returns:
            QuerySet: 현재 사용자의 활동 기록 리스트.
        """
        return UserActivity.objects.filter(user=self.request.user)


class DeleteAccountView(APIView):
    """
    현재 로그인한 사용자의 계정을 삭제하는 뷰입니다.
    """
    permission_classes = [IsAuthenticated]

    @delete_account_schema
    def delete(self, request):
        """
        현재 로그인한 사용자의 계정을 삭제합니다.
        
        Args:
            request (Request): 계정 삭제 요청.

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
    새로운 매니저 계정을 생성하는 뷰입니다. 관리자만 접근 가능합니다.
    """
    permission_classes = [IsAdminUser]

    @manager_creation_schema
    def post(self, request):
        """
        새로운 매니저 계정을 생성합니다.
        
        Args:
            request (Request): 매니저 계정 생성 요청 데이터.

        Returns:
            Response: 생성된 매니저 정보와 함께 성공 메시지 또는 오류 메시지.
        """
        serializer = ManagerCreationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # 매니저 계정 생성
            refresh = RefreshToken.for_user(user)  # 사용자 리프레시 토큰 생성
            return Response(
                {
                    "message": "Manager user created successfully",
                    "user": UserSerializer(user).data,  # 생성된 사용자 정보
                    "refresh": str(refresh),  # 리프레시 토큰
                    "access": str(refresh.access_token),  # 액세스 토큰
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserRoleView(APIView):
    """
    특정 사용자의 역할을 변경하는 뷰입니다. 관리자만 접근 가능합니다.
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        """
        특정 사용자의 역할을 변경합니다.
        
        Args:
            request (Request): 역할 변경 요청 데이터.
            user_id (int): 역할을 변경할 사용자 ID.

        Returns:
            Response: 변경된 사용자 정보와 함께 성공 메시지 또는 오류 메시지.
        """
        try:
            user = CustomUser.objects.get(id=user_id)  # 사용자 조회
            new_role = request.data.get("role")  # 새로운 역할
            if new_role not in ["student", "manager"]:
                return Response(
                    {"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST
                )
            user.role = new_role  # 역할 변경
            user.save()
            return Response(UserSerializer(user).data)  # 변경된 사용자 정보 반환
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    사용자 관리를 위한 ViewSet입니다.
    관리자는 모든 사용자에 접근할 수 있으며, 매니저는 학생만 볼 수 있습니다.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        요청자의 역할에 따라 사용자 목록을 필터링합니다.
        Returns:
            QuerySet: 필터링된 사용자 목록.
        """
        user = self.request.user
        if user.role == "admin":
            return CustomUser.objects.all()
        elif user.role == "manager":
            return CustomUser.objects.filter(role="student")
        else:
            return CustomUser.objects.filter(id=user.id)

    def get_permissions(self):
        """
        요청하는 액션에 따라 권한을 설정합니다.
        Returns:
            list: 해당 요청에 대한 권한 클래스 목록.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminUser]
        elif self.action == "list":
            self.permission_classes = [IsManagerOrAdminUser]
        elif self.action == "retrieve":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="page",
                description="페이지 번호",
                required=False,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name="page_size",
                description="페이지당 결과 수",
                required=False,
                type=OpenApiTypes.INT,
            ),
        ],
        responses={
            200: UserSerializer(many=True),  # 성공적으로 사용자 목록을 반환
            403: OpenApiTypes.STR,  # 권한 없음
            500: OpenApiTypes.STR,  # 서버 오류
        },
        description="모든 사용자 목록을 반환합니다. 관리자는 모든 사용자를, 매니저는 학생만 볼 수 있습니다.",
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=UserSerializer,  # 요청 시 사용하는 시리얼라이저
        responses={
            201: UserSerializer,  # 성공적으로 사용자 생성
            400: OpenApiTypes.OBJECT,  # 잘못된 요청
            403: OpenApiTypes.STR,  # 권한 없음
        },
        description="새로운 사용자를 생성합니다.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: UserSerializer,  # 성공적으로 사용자 정보 반환
            403: OpenApiTypes.STR,  # 권한 없음
            404: OpenApiTypes.STR,  # 사용자 찾기 실패
        },
        description="특정 사용자의 상세 정보를 반환합니다.",
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = CustomUser.objects.get(pk=kwargs["pk"])
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if request.user.role in ["admin", "manager"] or request.user.id == instance.id:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    @extend_schema(
        request=UserSerializer,  # 전체 업데이트 시 사용하는 시리얼라이저
        responses={
            200: UserSerializer,  # 성공적으로 사용자 정보 반환
            400: OpenApiTypes.OBJECT,  # 잘못된 요청
            403: OpenApiTypes.STR,  # 권한 없음
        },
        description="특정 사용자의 정보를 전체 업데이트합니다.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=UserSerializer,  # 부분 업데이트 시 사용하는 시리얼라이저
        responses={
            200: UserSerializer,  # 성공적으로 사용자 정보 반환
            400: OpenApiTypes.OBJECT,  # 잘못된 요청
            403: OpenApiTypes.STR,  # 권한 없음
        },
        description="특정 사용자의 정보를 부분 업데이트합니다.",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={
            204: None,  # 성공적으로 사용자 삭제
            403: OpenApiTypes.STR,  # 권한 없음
            404: OpenApiTypes.STR,  # 사용자 찾기 실패
        },
        description="특정 사용자를 삭제합니다.",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@extend_schema(
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiTypes.OBJECT,  # 성공적으로 사용자가 등록되었을 때 반환될 객체
        400: OpenApiTypes.OBJECT,  # 잘못된 요청일 경우의 오류 메시지
        500: OpenApiTypes.STR,  # 서버 오류 시 반환될 문자열 오류 메시지
    },
    description="새로운 사용자를 등록합니다. 등록 성공 시 사용자 정보와 액세스, 리프레시 토큰을 반환합니다.",
)
class RegisterView(generics.CreateAPIView):
    """
    새로운 사용자를 등록하는 뷰입니다.

    등록 성공 시 사용자 정보와 함께 액세스 토큰과 리프레시 토큰을 반환합니다.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        사용자를 등록하고, 사용자 정보와 토큰을 반환합니다.

        Args:
            request (Request): 사용자 등록 요청 데이터.

        Returns:
            Response: 사용자 정보 및 액세스, 리프레시 토큰.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    request=UserLoginSerializer,
    responses={
        200: OpenApiTypes.OBJECT,  # 성공적으로 로그인했을 때 반환될 객체
        400: OpenApiTypes.OBJECT,  # 잘못된 로그인 정보로 인한 오류 메시지
        401: OpenApiTypes.STR,  # 인증 실패(로그인 실패) 시 반환되는 문자열 오류 메시지
        500: OpenApiTypes.STR,  # 서버 오류 시 반환될 문자열 오류 메시지
    },
    description="사용자 로그인을 처리하고, 성공 시 사용자 정보와 액세스, 리프레시 토큰을 반환합니다.",
)
class LoginView(APIView):
    """
    사용자 로그인을 처리하는 뷰입니다.

    로그인 성공 시 사용자 정보와 함께 액세스 토큰과 리프레시 토큰을 반환합니다.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        사용자의 로그인 요청을 처리합니다.

        Args:
            request (Request): 로그인 요청 데이터.

        Returns:
            Response: 사용자 정보 및 액세스, 리프레시 토큰.
        """
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    request={"refresh_token": str},
    responses={200: {"description": "Successfully logged out."}},
    description="사용자 로그아웃을 처리합니다.",
)
class LogoutView(APIView):
    """
    사용자 로그아웃을 처리하는 뷰입니다.

    로그아웃 성공 시 리프레시 토큰을 블랙리스트에 추가합니다.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={
        200: UserSerializer,  # 성공적으로 사용자 프로필을 조회할 때 반환되는 객체
        400: OpenApiTypes.OBJECT,  # 잘못된 요청 시 반환될 오류 메시지
        404: OpenApiTypes.STR,  # 프로필을 찾을 수 없을 때 반환될 메시지
    },
    description="현재 로그인한 사용자의 프로필 정보를 조회하거나 수정합니다.",
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    현재 로그인한 사용자의 프로필 정보를 조회하거나 수정하는 뷰입니다.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        현재 로그인한 사용자 객체를 반환합니다.

        Returns:
            User: 현재 요청의 사용자 객체.
        """
        return self.request.user


@extend_schema(
    responses={
        200: UserActivitySerializer(
            many=True
        ),  # 성공적으로 활동 기록을 조회할 때 반환되는 객체 리스트
        400: OpenApiTypes.OBJECT,  # 잘못된 요청 시 반환될 오류 메시지
        404: OpenApiTypes.STR,  # 요청한 활동 기록을 찾을 수 없을 때 반환될 메시지
    },
    description="현재 로그인한 사용자의 활동 기록을 조회합니다.",
)
class UserActivityListView(generics.ListAPIView):
    """
    현재 로그인한 사용자의 활동 기록을 조회하는 뷰입니다.
    """

    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        현재 로그인한 사용자의 활동 기록을 반환합니다.

        Returns:
            QuerySet: 현재 사용자의 활동 기록 리스트.
        """
        return UserActivity.objects.filter(user=self.request.user)


@extend_schema(
    responses={
        204: None,  # 계정 삭제 성공 시 응답 코드
        400: OpenApiTypes.OBJECT,  # 잘못된 요청 시 반환될 오류 메시지
        404: OpenApiTypes.STR,  # 요청한 사용자를 찾을 수 없을 때 반환될 메시지
    },
    description="현재 로그인한 사용자의 계정을 삭제합니다.",
)
class DeleteAccountView(APIView):
    """
    현재 로그인한 사용자의 계정을 삭제하는 뷰입니다.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """
        현재 로그인한 사용자의 계정을 삭제합니다.

        Args:
            request (Request): 계정 삭제 요청.

        Returns:
            Response: 계정 삭제 성공 메시지.
        """
        user = request.user
        user.delete()
        return Response(
            {"detail": "Account successfully deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema(
    request=ManagerCreationSerializer,  # 매니저 생성 요청 시 사용하는 직렬화기
    responses={
        201: UserSerializer,  # 성공적으로 매니저 계정을 생성할 때 반환되는 객체
        400: OpenApiTypes.OBJECT,  # 잘못된 요청 시 반환될 오류 메시지
    },
    description="새로운 매니저 계정을 생성합니다.",
)
class ManagerCreationView(APIView):
    """
    새로운 매니저 계정을 생성하는 뷰입니다. 관리자만 접근 가능합니다.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        """
        새로운 매니저 계정을 생성합니다.

        Args:
            request (Request): 매니저 계정 생성 요청 데이터.

        Returns:
            Response: 생성된 매니저 정보와 함께 성공 메시지 또는 오류 메시지.
        """
        serializer = ManagerCreationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # 매니저 계정 생성
            refresh = RefreshToken.for_user(user)  # 사용자 리프레시 토큰 생성
            return Response(
                {
                    "message": "Manager user created successfully",
                    "user": UserSerializer(user).data,  # 생성된 사용자 정보
                    "refresh": str(refresh),  # 리프레시 토큰
                    "access": str(refresh.access_token),  # 액세스 토큰
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="user_id", description="사용자 ID", required=True, type=int
        )
    ],
    request={"role": str},  # 역할 변경 요청 시 사용하는 데이터 구조
    responses={
        200: UserSerializer,  # 성공적으로 역할을 변경할 때 반환되는 객체
        400: OpenApiTypes.OBJECT,  # 잘못된 요청 시 반환될 오류 메시지
        404: OpenApiTypes.STR,  # 요청한 사용자를 찾을 수 없을 때 반환될 메시지
    },
    description="특정 사용자의 역할을 변경합니다.",
)
class ChangeUserRoleView(APIView):
    """
    특정 사용자의 역할을 변경하는 뷰입니다. 관리자만 접근 가능합니다.
    """

    permission_classes = [IsAdminUser]

    @change_user_role_schema
    def patch(self, request, user_id):
        """
        특정 사용자의 역할을 변경합니다.

        Args:
            request (Request): 역할 변경 요청 데이터.
            user_id (int): 역할을 변경할 사용자 ID.

        Returns:
            Response: 변경된 사용자 정보와 함께 성공 메시지 또는 오류 메시지.
        """
        try:
            user = CustomUser.objects.get(id=user_id)  # 사용자 조회
            new_role = request.data.get("role")  # 새로운 역할
            if new_role not in ["student", "manager"]:
                return Response(
                    {"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST
                )
            user.role = new_role  # 역할 변경
            user.save()
            return Response(UserSerializer(user).data)  # 변경된 사용자 정보 반환
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class RoleCheckView(APIView):
    """
    현재 로그인한 사용자의 역할을 확인하는 뷰입니다.
    """

    permission_classes = [IsAuthenticated]

    @role_check_schema 
    def get(self, request):
        """
        현재 로그인한 사용자의 역할을 반환합니다.

        Returns:
            Response: 사용자의 역할 정보.
        """
        user = request.user
        return Response({"role": user.role})

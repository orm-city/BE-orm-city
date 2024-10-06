from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserManagementViewSet,
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    UserActivityListView,
    DeleteAccountView,
    ManagerCreationView,
    ChangeUserRoleView,
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


router = DefaultRouter()
router.register(r"users", UserManagementViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("activity/", UserActivityListView.as_view(), name="activity"),
    path("delete/", DeleteAccountView.as_view(), name="delete"),
    path("create-manager/", ManagerCreationView.as_view(), name="create_manager"),
    path(
        "change-role/<int:user_id>/", ChangeUserRoleView.as_view(), name="change_role"
    ),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

"""
사용자 관리, 인증, 프로필, 활동, 계정 삭제 및 관리자 생성 등 사용자 관련 기능에 대한 UㄴRL 패턴을 정의하는 모듈.

- `UserManagementViewSet`: 사용자 목록 관리.
- `RegisterView`: 사용자 등록.
- `LoginView`: 사용자 로그인.
- `LogoutView`: 사용자 로그아웃.
- `UserProfileView`: 사용자 프로필 조회 및 수정.
- `UserActivityListView`: 사용자 활동 로그 조회.
- `DeleteAccountView`: 사용자 계정 삭제.
- `ManagerCreationView`: 관리자 계정 생성.
- `ChangeUserRoleView`: 사용자의 역할 변경.

변수:
    router (DefaultRouter): 기본 라우터로 `UserManagementViewSet`을 등록하여 기본 경로 설정.
    urlpatterns (list): URL 경로 및 해당하는 뷰를 정의한 리스트.

URL 경로:
    - "register/": 사용자 등록.
    - "login/": 로그인 처리.
    - "logout/": 로그아웃 처리.
    - "profile/": 사용자 프로필 조회 및 수정.
    - "activity/": 사용자의 활동 로그 조회.
    - "delete/": 계정 삭제.
    - "create-manager/": 관리자 계정 생성.
    - "change-role/<int:user_id>/": 사용자의 역할 변경.
"""

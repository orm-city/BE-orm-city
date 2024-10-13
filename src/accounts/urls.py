from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
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
    RoleCheckView,
)


router = DefaultRouter()
router.register(r"users", UserManagementViewSet, basename="user")

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
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("check-role/", RoleCheckView.as_view(), name="check-role"),
]

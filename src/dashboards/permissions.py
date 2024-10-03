from rest_framework.permissions import BasePermission
from core.permissions import IsAdminUser


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return IsAdminUser().has_permission(request, view)


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or IsAdminUser().has_permission(request, view)

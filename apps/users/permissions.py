"""Custom DRF permissions."""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow access only to users with ADMIN role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )


class IsUser(BasePermission):
    """Allow access only to users with USER role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'USER'
        )


class IsAdminOrReadOnly(BasePermission):
    """Allow read-only access to any authenticated user; write access to admins only."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.role == 'ADMIN'

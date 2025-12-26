from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .enums import RoleChoices

class BaseRolePermission(BasePermission):
    allowed_roles: tuple = ()

    def has_permission(self, request, view):
        user = request.user
        return (
            user
            and user.is_authenticated
            and user.role in self.allowed_roles
        )

class IsAdminOrManager(BaseRolePermission):
    allowed_roles = (RoleChoices.ADMIN, RoleChoices.MANAGER)

    def has_object_permission(self, request, view, obj):
        updater = request.user
        new_role = request.data.get('role')

        if updater.role == RoleChoices.MANAGER:
            if obj.role != RoleChoices.DEVELOPER:
                raise PermissionDenied("Manager can update only developer")
            if new_role and new_role != RoleChoices.DEVELOPER:
                raise PermissionDenied("Manager can assigned only developer")
        return True
        
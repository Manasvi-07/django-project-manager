from rest_framework.permissions import BasePermission
from account.enums import RoleChoices

class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [RoleChoices.ADMIN, RoleChoices.MANAGER]
    
class IsAdminManagerOrTaskOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == RoleChoices.ADMIN:
            return True
        if user.role == RoleChoices.MANAGER:
            return hasattr(obj, "project") and obj.project.owner == user
        if user.role == RoleChoices.DEVELOPER:
            return user in obj.assigned.all()
        return False
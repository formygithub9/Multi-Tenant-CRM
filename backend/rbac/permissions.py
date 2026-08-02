from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from authorization.models import Permission
from rbac.models import Membership, RolePermission

class HasPermission(BasePermission):

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):

        required_permission = getattr(view, "required_permission", None)

        if not required_permission:
            return True

        membership = Membership.objects.filter(user=request.user,is_active=True,).select_related("role").first()

        if not membership:
            self.message = "User is not assigned to any tenant."
            return False

        permission = Permission.objects.filter(code__iexact=required_permission,is_active=True,).first()

        if not permission:
            self.message = "Permission does not exist."
            return False

        role_permission = RolePermission.objects.filter(role=membership.role,permission=permission,).exists()

        if not role_permission:
            self.message = "You do not have permission to perform this action."
            return False
        
        return True
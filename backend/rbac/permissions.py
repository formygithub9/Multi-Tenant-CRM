from rest_framework.permissions import BasePermission

from authorization.models import Permission
from rbac.models import Membership, RolePermission


class HasPermission(BasePermission):

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):

        required_permissions = getattr(
            view,
            "required_permissions",
            {},
        )

        required_permission = required_permissions.get(
            request.method,
        )

        if not required_permission:
            return True

        tenant_id = getattr(
            request,
            "tenant_id",
            None,
        )

        if not tenant_id:
            self.message = "Tenant context is required."
            return False

        membership = (
            Membership.objects
            .select_related("role")
            .filter(
                user=request.user,
                tenant_id=tenant_id,
                is_active=True,
            )
            .first()
        )

        if not membership:
            self.message = (
                "You are not a member of this tenant."
            )
            return False

        permission = (
            Permission.objects
            .filter(
                code__iexact=required_permission,
                is_active=True,
            )
            .first()
        )

        if not permission:
            self.message = "Permission does not exist."
            return False

        has_permission = (
            RolePermission.objects
            .filter(
                role=membership.role,
                permission=permission,
                is_active=True,
            )
            .exists()
        )

        if not has_permission:
            self.message = (
                "You do not have permission "
                "to perform this action."
            )
            return False

        return True
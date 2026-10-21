import inspect

from rest_framework.permissions import BasePermission

from authorization.models import Permission
from rbac.models import Membership, RolePermission


class HasPermission(BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if request.method == "OPTIONS":
            return True

        required_permissions = getattr(view, "required_permissions", None)

        if required_permissions is not None:
            required_permission = required_permissions.get(request.method)

            if request.method == "HEAD" and not required_permission:
                required_permission = required_permissions.get("GET")
        else:
            permission_getter = getattr(view, "get_required_permission", None)

            if callable(permission_getter):
                parameters = inspect.signature(permission_getter).parameters

                if parameters:
                    required_permission = permission_getter(
                        request,
                        *getattr(view, "args", ()),
                        **getattr(view, "kwargs", {}),
                    )
                else:
                    required_permission = permission_getter()
            else:
                required_permission = getattr(view, "required_permission", None)

        if not required_permission:
            self.message = "Required permission is not configured for this action."
            return False

        tenant_id = getattr(request, "tenant_id", None)

        if not tenant_id:
            self.message = "Tenant context is required."
            return False

        membership = (
            Membership.objects.select_related("role")
            .filter(user=request.user, tenant_id=tenant_id, is_active=True)
            .first()
        )

        if not membership:
            self.message = "You are not a member of this tenant."
            return False

        permission = Permission.objects.filter(
            code__iexact=required_permission,
            is_active=True,
        ).first()

        if not permission:
            self.message = "Permission does not exist."
            return False

        has_permission = RolePermission.objects.filter(
            role=membership.role,
            permission=permission,
            is_active=True,
        ).exists()

        if not has_permission:
            self.message = "You do not have permission to perform this action."
            return False

        return True
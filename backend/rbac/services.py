from django.db.models import Q
from rbac.models import Role, Membership, RolePermission
from authorization.models import Permission

class RoleService:

    DEFAULT_ROLES = (
        "Admin",
        "Manager",
        "Sales",
        "Support",
    )

    @classmethod
    def create_default_roles(cls, tenant):

        roles = {}

        for role_name in cls.DEFAULT_ROLES:

            role = Role.objects.create(
                tenant_id=tenant.id,
                name=role_name,
            )
            RolePermissionService.assign_permissions(role)
            roles[role_name] = role

        return roles

class MembershipService:

    @staticmethod
    def create_membership(user, tenant, role):

        return Membership.objects.create(
            user=user,
            tenant_id=tenant.id,
            role=role,
        )

class RolePermissionService:

    ROLE_PERMISSION_MAP = {
        "Admin": "ALL",

        "Manager": (
            "view",
            "create",
            "update",
            "export",
        ),

        "Sales": (
            "view",
            "create",
            "update",
        ),

        "Support": (
            "view",
        ),
    }

    @classmethod
    def assign_permissions(cls, role):

        permission_config = cls.ROLE_PERMISSION_MAP.get(role.name)

        if not permission_config:
            return

        if permission_config == "ALL":

            permissions = Permission.objects.filter(is_active=True)

        else:
            query = Q()

            for permission_name in permission_config:
                query |= Q(permission_type__name__iexact=permission_name)

            permissions = Permission.objects.filter(
                query,
                is_active=True,
            )

        for permission in permissions:

            RolePermission.objects.get_or_create(
                role=role,
                permission=permission,
            )
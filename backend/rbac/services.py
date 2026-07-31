from rbac.models import Role
from rbac.models import Membership

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
                tenant=tenant,
                name=role_name,
            )

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
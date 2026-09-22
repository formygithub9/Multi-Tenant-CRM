from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from authorization.models import Permission
from rbac.models import Membership, Role, RolePermission
from rbac.services import RolePermissionService
from tenants.models import Tenant


class RBACPermissionMatrixTest(TestCase):

    databases = {
        "default",
        "shared_db",
    }

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.using("default").create(
            name="RBAC Test Company",
            company_mobile="9999999999",
            database_alias="shared_db",
        )

        cls.admin_user = User.objects.create_user(
            username="rbac_admin",
            email="admin@example.com",
            password="TestPass123!",
        )

        cls.manager_user = User.objects.create_user(
            username="rbac_manager",
            email="manager@example.com",
            password="TestPass123!",
        )

        cls.sales_user = User.objects.create_user(
            username="rbac_sales",
            email="sales@example.com",
            password="TestPass123!",
        )

        cls.support_user = User.objects.create_user(
            username="rbac_support",
            email="support@example.com",
            password="TestPass123!",
        )

        cls.admin_role = Role.objects.using("shared_db").create(
            tenant_id=cls.tenant.id,
            name="Admin",
        )

        cls.manager_role = Role.objects.using("shared_db").create(
            tenant_id=cls.tenant.id,
            name="Manager",
        )

        cls.sales_role = Role.objects.using("shared_db").create(
            tenant_id=cls.tenant.id,
            name="Sales",
        )

        cls.support_role = Role.objects.using("shared_db").create(
            tenant_id=cls.tenant.id,
            name="Support",
        )

        RolePermissionService.assign_permissions(cls.admin_role)
        RolePermissionService.assign_permissions(cls.manager_role)
        RolePermissionService.assign_permissions(cls.sales_role)
        RolePermissionService.assign_permissions(cls.support_role)

        Membership.objects.using("shared_db").create(
            user=cls.admin_user,
            tenant_id=cls.tenant.id,
            role=cls.admin_role,
        )

        Membership.objects.using("shared_db").create(
            user=cls.manager_user,
            tenant_id=cls.tenant.id,
            role=cls.manager_role,
        )

        Membership.objects.using("shared_db").create(
            user=cls.sales_user,
            tenant_id=cls.tenant.id,
            role=cls.sales_role,
        )

        Membership.objects.using("shared_db").create(
            user=cls.support_user,
            tenant_id=cls.tenant.id,
            role=cls.support_role,
        )

    def test_admin_has_all_permissions(self):
        permissions = RolePermission.objects.using("shared_db").filter(
            role=self.admin_role,
            is_active=True,
        )

        total_permissions = Permission.objects.using("shared_db").filter(
            is_active=True,
        ).count()

        self.assertEqual(
            permissions.count(),
            total_permissions,
        )

    def test_manager_has_expected_permissions(self):
        permissions = set(
            RolePermission.objects.using("shared_db")
            .filter(
                role=self.manager_role,
                is_active=True,
            )
            .values_list(
                "permission__permission_type__name",
                flat=True,
            )
        )

        self.assertEqual(
            permissions,
            {
                "View",
                "Create",
                "Update",
                "Export",
            },
        )

    def test_sales_has_expected_permissions(self):
        permissions = set(
            RolePermission.objects.using("shared_db")
            .filter(
                role=self.sales_role,
                is_active=True,
            )
            .values_list(
                "permission__permission_type__name",
                flat=True,
            )
        )

        self.assertEqual(
            permissions,
            {
                "View",
                "Create",
                "Update",
            },
        )

    def test_support_has_only_view_permission(self):
        permissions = set(
            RolePermission.objects.using("shared_db")
            .filter(
                role=self.support_role,
                is_active=True,
            )
            .values_list(
                "permission__permission_type__name",
                flat=True,
            )
        )

        self.assertEqual(
            permissions,
            {
                "View",
            },
        )
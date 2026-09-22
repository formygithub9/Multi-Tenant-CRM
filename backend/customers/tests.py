from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User

from authorization.models import Permission

from common.models import Sequence

from core.exceptions import NotFoundException

from customers.models import Customer
from customers.services import CustomerService

from rbac.models import Membership, Role, RolePermission

from tenants.models import Tenant


class CustomerTenantIsolationTest(TestCase):

    databases = {"default", "shared_db"}

    def setUp(self):

        self.tenant_a = Tenant.objects.using("default").create(
            name="Company A",
            company_mobile="6666666661",
            company_email="customer_a@company.com",
            database_alias="shared_db",
        )

        self.tenant_b = Tenant.objects.using("default").create(
            name="Company B",
            company_mobile="6666666662",
            company_email="customer_b@company.com",
            database_alias="shared_db",
        )

        self.customer_a = Customer.objects.using(
            "shared_db"
        ).create(
            tenant_id=self.tenant_a.id,
            customer_code="CUS000001",
            customer_type=Customer.CustomerType.BUSINESS,
            contact_name="Rahul Sharma",
            company_name="Company A",
            email="rahul@a.com",
            mobile="9999999991",
            gst_number="GST-A-001",
        )

        self.customer_b = Customer.objects.using(
            "shared_db"
        ).create(
            tenant_id=self.tenant_b.id,
            customer_code="CUS000001",
            customer_type=Customer.CustomerType.BUSINESS,
            contact_name="Amit Verma",
            company_name="Company B",
            email="amit@b.com",
            mobile="9999999992",
            gst_number="GST-B-001",
        )

    def test_tenant_only_gets_own_customers(self):

        customers = CustomerService.get_customers(
            tenant_id=self.tenant_a.id,
        )

        customer_ids = list(
            customers.values_list(
                "id",
                flat=True,
            )
        )

        self.assertIn(
            self.customer_a.id,
            customer_ids,
        )

        self.assertNotIn(
            self.customer_b.id,
            customer_ids,
        )

    def test_tenant_cannot_access_other_tenant_customer(self):

        with self.assertRaises(NotFoundException) as context:

            CustomerService.get_customer_by_id(
                tenant_id=self.tenant_a.id,
                customer_id=self.customer_b.id,
            )

        self.assertEqual(
            str(context.exception),
            "Customer not found.",
        )

    def test_inactive_customer_cannot_be_accessed(self):

        self.customer_a.is_active = False

        self.customer_a.save(
            using="shared_db",
            update_fields=["is_active"],
        )

        with self.assertRaises(NotFoundException):

            CustomerService.get_customer_by_id(
                tenant_id=self.tenant_a.id,
                customer_id=self.customer_a.id,
            )


class CustomerAPITest(APITestCase):

    databases = {"default", "shared_db"}

    def setUp(self):

        self.tenant_a = Tenant.objects.using("default").create(
            name="Company A",
            company_mobile="5555555551",
            company_email="api_customer_a@company.com",
            database_alias="shared_db",
        )

        self.tenant_b = Tenant.objects.using("default").create(
            name="Company B",
            company_mobile="5555555552",
            company_email="api_customer_b@company.com",
            database_alias="shared_db",
        )

        self.role = Role.objects.using("shared_db").create(
            name="Admin",
            tenant_id=self.tenant_a.id,
        )

        permission_codes = [
            "customers.view",
            "customers.create",
            "customers.update",
            "customers.delete",
        ]

        permissions = Permission.objects.using(
            "shared_db"
        ).filter(
            code__in=permission_codes,
            is_active=True,
        )

        RolePermission.objects.using(
            "shared_db"
        ).bulk_create(
            [
                RolePermission(
                    role=self.role,
                    permission=permission,
                )
                for permission in permissions
            ]
        )

        self.user = User.objects.create_user(
            username="customeruser",
            email="customeruser@test.com",
            password="password123",
        )

        self.membership = Membership.objects.using(
            "shared_db"
        ).create(
            user=self.user,
            tenant_id=self.tenant_a.id,
            role=self.role,
        )

        self.client.force_authenticate(
            user=self.user,
        )

        self.client.defaults[
            "HTTP_X_COMPANY_MOBILE"
        ] = self.tenant_a.company_mobile

    def test_create_customer(self):

        response = self.client.post(
            "/api/customers/",
            {
                "customer_type": "BUSINESS",
                "contact_name": "Rahul Sharma",
                "company_name": "ABC Technologies",
                "email": "rahul@abc.com",
                "mobile": "9999999999",
                "gst_number": "GST-001",
                "pan_number": "ABCDE1234F",
                "remarks": "Test customer",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            response.data["success"],
        )

        self.assertEqual(
            response.data["data"]["contact_name"],
            "Rahul Sharma",
        )

    def test_customer_list_only_returns_current_tenant(self):

        Customer.objects.using("shared_db").create(
            tenant_id=self.tenant_a.id,
            customer_code="CUS000001",
            customer_type=Customer.CustomerType.BUSINESS,
            contact_name="Rahul Sharma",
            company_name="Company A",
            gst_number="GST-A-001",
        )

        Customer.objects.using("shared_db").create(
            tenant_id=self.tenant_b.id,
            customer_code="CUS000001",
            customer_type=Customer.CustomerType.BUSINESS,
            contact_name="Amit Verma",
            company_name="Company B",
            gst_number="GST-B-001",
        )

        response = self.client.get(
            "/api/customers/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response_data = response.data["results"]

        returned_names = [
            customer["contact_name"]
            for customer in response_data
        ]

        self.assertIn(
            "Rahul Sharma",
            returned_names,
        )

        self.assertNotIn(
            "Amit Verma",
            returned_names,
        )

    def test_other_tenant_customer_returns_not_found(self):

        customer_b = Customer.objects.using(
            "shared_db"
        ).create(
            tenant_id=self.tenant_b.id,
            customer_code="CUS000001",
            customer_type=Customer.CustomerType.BUSINESS,
            contact_name="Amit Verma",
            company_name="Company B",
            gst_number="GST-B-001",
        )

        response = self.client.get(
            f"/api/customers/{customer_b.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_update_customer(self):

        customer = Customer.objects.using(
            "shared_db"
        ).create(
            tenant_id=self.tenant_a.id,
            customer_code="CUS000001",
            customer_type=Customer.CustomerType.BUSINESS,
            contact_name="Rahul Sharma",
            company_name="Company A",
            gst_number="GST-A-001",
        )

        response = self.client.patch(
            f"/api/customers/{customer.id}/",
            {
                "contact_name": "Rahul Updated",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        customer.refresh_from_db(
            using="shared_db"
        )

        self.assertEqual(
            customer.contact_name,
            "Rahul Updated",
        )

    def test_delete_customer_soft_deletes(self):

        customer = Customer.objects.using(
            "shared_db"
        ).create(
            tenant_id=self.tenant_a.id,
            customer_code="CUS000001",
            customer_type=Customer.CustomerType.BUSINESS,
            contact_name="Rahul Sharma",
            company_name="Company A",
            gst_number="GST-A-001",
        )

        response = self.client.delete(
            f"/api/customers/{customer.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        customer.refresh_from_db(
            using="shared_db"
        )

        self.assertFalse(
            customer.is_active,
        )

    def test_unauthenticated_user_cannot_access_customers(self):

        self.client.force_authenticate(
            user=None,
        )

        response = self.client.get(
            "/api/customers/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
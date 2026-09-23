from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from common.models import Sequence
from rbac.models import Membership, Role
from rbac.services import RolePermissionService
from tenants.models import Tenant
from vendors.models import Vendor


class VendorAPITest(TestCase):

    databases = {
        "default",
        "shared_db",
    }

    @classmethod
    def setUpTestData(cls):

        cls.tenant_a = Tenant.objects.using("default").create(
            name="Vendor Tenant A",
            company_email="vendora@tenant.com",
            company_mobile="9000000001",
            database_alias="shared_db",
        )

        cls.tenant_b = Tenant.objects.using("default").create(
            name="Vendor Tenant B",
            company_email="vendorb@tenant.com",
            company_mobile="9000000002",
            database_alias="shared_db",
        )

        cls.user_a = User.objects.create_user(
            username="vendor_user_a",
            email="vendora@example.com",
            password="TestPass123!",
        )

        cls.user_b = User.objects.create_user(
            username="vendor_user_b",
            email="vendorb@example.com",
            password="TestPass123!",
        )

        cls.role_a = Role.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            name="Admin",
        )

        cls.role_b = Role.objects.using("shared_db").create(
            tenant_id=cls.tenant_b.id,
            name="Admin",
        )

        RolePermissionService.assign_permissions(
            cls.role_a
        )

        RolePermissionService.assign_permissions(
            cls.role_b
        )

        Membership.objects.using("shared_db").create(
            user=cls.user_a,
            tenant_id=cls.tenant_a.id,
            role=cls.role_a,
        )

        Membership.objects.using("shared_db").create(
            user=cls.user_b,
            tenant_id=cls.tenant_b.id,
            role=cls.role_b,
        )

        Sequence.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            sequence_type=Sequence.SequenceType.VENDOR,
            next_number=2,
        )

        cls.vendor_a = Vendor.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            vendor_code="VEN000001",
            vendor_type=Vendor.VendorType.BUSINESS,
            contact_name="Vendor A",
            company_name="Company A",
            email="vendora@company.com",
            gst_number="GST123456",
        )

        cls.vendor_b = Vendor.objects.using("shared_db").create(
            tenant_id=cls.tenant_b.id,
            vendor_code="VEN000001",
            vendor_type=Vendor.VendorType.BUSINESS,
            contact_name="Vendor B",
            company_name="Company B",
            email="vendorb@company.com",
            gst_number="GST654321",
        )

    def setUp(self):

        self.client = APIClient()

        self.client.force_authenticate(
            user=self.user_a
        )

        self.client.defaults[
            "HTTP_X_COMPANY_MOBILE"
        ] = self.tenant_a.company_mobile

    def test_list_vendors(self):

        response = self.client.get(
            "/api/vendors/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["vendor_code"],
            "VEN000001",
        )

    def test_get_vendor(self):

        response = self.client.get(
            f"/api/vendors/{self.vendor_a.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["data"]["vendor_code"],
            "VEN000001",
        )

    def test_cross_tenant_vendor_is_not_visible(self):

        response = self.client.get(
            f"/api/vendors/{self.vendor_b.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_create_vendor(self):

        response = self.client.post(
            "/api/vendors/",
            {
                "vendor_type": "BUSINESS",
                "contact_name": "New Vendor",
                "company_name": "New Vendor Company",
                "email": "newvendor@example.com",
                "mobile": "9999999999",
                "gst_number": "GST999999",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["data"]["vendor_code"],
            "VEN000002",
        )

        vendor = Vendor.objects.using(
            "shared_db"
        ).get(
            id=response.data["data"]["id"]
        )

        self.assertEqual(
            vendor.tenant_id,
            self.tenant_a.id,
        )

    def test_update_vendor(self):

        response = self.client.patch(
            f"/api/vendors/{self.vendor_a.id}/",
            {
                "contact_name": "Updated Vendor",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.vendor_a.refresh_from_db(
            using="shared_db"
        )

        self.assertEqual(
            self.vendor_a.contact_name,
            "Updated Vendor",
        )

    def test_delete_vendor(self):

        response = self.client.delete(
            f"/api/vendors/{self.vendor_a.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.vendor_a.refresh_from_db(
            using="shared_db"
        )

        self.assertFalse(
            self.vendor_a.is_active
        )

    def test_unauthenticated_access_is_denied(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            "/api/vendors/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_business_vendor_requires_gst(self):

        response = self.client.post(
            "/api/vendors/",
            {
                "vendor_type": "BUSINESS",
                "contact_name": "No GST Vendor",
                "company_name": "No GST Company",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "gst_number",
            response.data["errors"],
        )

    def test_individual_vendor_rejects_gst(self):

        response = self.client.post(
            "/api/vendors/",
            {
                "vendor_type": "INDIVIDUAL",
                "contact_name": "Individual Vendor",
                "gst_number": "GST123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "gst_number",
            response.data["errors"],
        )
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from common.models import Sequence
from rbac.models import Membership, Role
from rbac.services import RolePermissionService
from tenants.models import Tenant
from products.models import Product


class ProductAPITest(TestCase):

    databases = {"default","shared_db",}

    @classmethod
    def setUpTestData(cls):

        cls.tenant_a = Tenant.objects.using(
            "default"
        ).create(
            name="Product Tenant A",
            company_email="producta@tenant.com",
            company_mobile="9100000001",
            database_alias="shared_db",
        )

        cls.tenant_b = Tenant.objects.using(
            "default"
        ).create(
            name="Product Tenant B",
            company_email="productb@tenant.com",
            company_mobile="9100000002",
            database_alias="shared_db",
        )

        cls.user_a = User.objects.create_user(
            username="product_user_a",
            email="producta@example.com",
            password="TestPass123!",
        )

        cls.role_a = Role.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_a.id,
            name="Admin",
        )

        RolePermissionService.assign_permissions(cls.role_a)

        Membership.objects.using(
            "shared_db"
        ).create(
            user=cls.user_a,
            tenant_id=cls.tenant_a.id,
            role=cls.role_a,
        )

        Sequence.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_a.id,
            sequence_type=(
                Sequence.SequenceType.PRODUCT
            ),
            next_number=2,
        )

        cls.product_a = Product.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_a.id,
            product_code="PROD000001",
            product_type=Product.ProductType.GOODS,
            name="Product A",
            sku="SKU-A",
            unit="PCS",
            hsn_code="8471",
            tax_rate=18,
            purchase_price=500,
            selling_price=750,
        )

        cls.product_b = Product.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_b.id,
            product_code="PROD000001",
            product_type=Product.ProductType.GOODS,
            name="Product B",
            sku="SKU-B",
            unit="PCS",
            hsn_code="8471",
            tax_rate=18,
            purchase_price=600,
            selling_price=900,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user_a)
        self.client.defaults["HTTP_X_COMPANY_MOBILE"] = self.tenant_a.company_mobile

    def test_list_products(self):

        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(len(response.data["results"]),1,)
        self.assertEqual(response.data["results"][0]["product_code"],"PROD000001",)

    def test_get_product(self):

        response = self.client.get(f"/api/products/{self.product_a.id}/")
        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(response.data["data"]["product_code"],"PROD000001",)

    def test_cross_tenant_product_is_not_visible(self):

        response = self.client.get(
            f"/api/products/{self.product_b.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_create_product(self):

        response = self.client.post(
            "/api/products/",
            {
                "product_type": "GOODS",
                "name": "New Product",
                "sku": "SKU-NEW",
                "description": "New product",
                "unit": "PCS",
                "hsn_code": "8471",
                "tax_rate": "18.00",
                "purchase_price": "100.00",
                "selling_price": "150.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["data"]["product_code"],
            "PROD000002",
        )

        product = Product.objects.using(
            "shared_db"
        ).get(
            id=response.data["data"]["id"]
        )

        self.assertEqual(
            product.tenant_id,
            self.tenant_a.id,
        )

    def test_update_product(self):

        response = self.client.patch(
            f"/api/products/{self.product_a.id}/",
            {
                "name": "Updated Product",
                "selling_price": "850.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.product_a.refresh_from_db(
            using="shared_db"
        )

        self.assertEqual(
            self.product_a.name,
            "Updated Product",
        )

        self.assertEqual(
            self.product_a.selling_price,
            850,
        )

    def test_delete_product(self):

        response = self.client.delete(
            f"/api/products/{self.product_a.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.product_a.refresh_from_db(
            using="shared_db"
        )

        self.assertFalse(
            self.product_a.is_active
        )

    def test_unauthenticated_access_is_denied(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            "/api/products/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_negative_price_is_rejected(self):

        response = self.client.post(
            "/api/products/",
            {
                "product_type": "GOODS",
                "name": "Invalid Product",
                "unit": "PCS",
                "purchase_price": "-10",
                "selling_price": "100",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "purchase_price",
            response.data["errors"],
        )

    def test_invalid_tax_rate_is_rejected(self):

        response = self.client.post(
            "/api/products/",
            {
                "product_type": "GOODS",
                "name": "Invalid Tax Product",
                "unit": "PCS",
                "tax_rate": "101",
                "purchase_price": "100",
                "selling_price": "150",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "tax_rate",
            response.data["errors"],
        )

    def test_product_search(self):

        response = self.client.get(
            "/api/products/?search=SKU-A"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(response.data["results"][0]["sku"],"SKU-A",)
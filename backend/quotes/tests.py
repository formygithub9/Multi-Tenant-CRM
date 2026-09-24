from django.test import TestCase
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from authorization.models import Permission
from common.models import Sequence
from customers.models import Customer
from deals.models import Deal
from products.models import Product
from quotes.models import Quote, QuoteItem
from rbac.models import Membership, Role, RolePermission
from tenants.models import Tenant


class QuoteAPITest(TestCase):

    databases = {"default", "shared_db"}

    @classmethod
    def setUpTestData(cls):
        cls.tenant_a = Tenant.objects.using("default").create(
            name="Quote Tenant A",
            company_email="quotea@tenant.com",
            company_mobile="9100000201",
            database_alias="shared_db",
        )

        cls.tenant_b = Tenant.objects.using("default").create(
            name="Quote Tenant B",
            company_email="quoteb@tenant.com",
            company_mobile="9100000202",
            database_alias="shared_db",
        )

        cls.user_a = User.objects.create_user(
            username="quote_user_a",
            email="quotea@example.com",
            password="TestPass123!",
        )

        cls.role_a = Role.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            name="Admin",
        )

        quote_permissions = Permission.objects.using(
            "shared_db"
        ).filter(
            code__in=[
                "quotes.view",
                "quotes.create",
                "quotes.update",
                "quotes.delete",
                "quotes.approve",
            ],
            is_active=True,
        )

        RolePermission.objects.using(
            "shared_db"
        ).bulk_create(
            [
                RolePermission(
                    role=cls.role_a,
                    permission=permission,
                )
                for permission in quote_permissions
            ]
        )

        Membership.objects.using("shared_db").create(
            user=cls.user_a,
            tenant_id=cls.tenant_a.id,
            role=cls.role_a,
        )

        Sequence.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            sequence_type=Sequence.SequenceType.QUOTE,
            next_number=2,
        )

        cls.customer_a = Customer.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_a.id,
            customer_code="CUS000001",
            customer_type="BUSINESS",
            contact_name="Rahul Sharma",
            company_name="ABC Technologies",
            email="rahul@abc.com",
            mobile="9999999999",
        )

        cls.customer_b = Customer.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_b.id,
            customer_code="CUS000001",
            customer_type="BUSINESS",
            contact_name="Amit Verma",
            company_name="XYZ Technologies",
            email="amit@xyz.com",
            mobile="8888888888",
        )

        cls.product_a = Product.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_a.id,
            product_code="PROD000001",
            product_type=Product.ProductType.GOODS,
            name="Laptop",
            sku="LAP-001",
            unit="PCS",
            hsn_code="8471",
            tax_rate=18,
            purchase_price=40000,
            selling_price=50000,
        )

        cls.product_b = Product.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_b.id,
            product_code="PROD000001",
            product_type=Product.ProductType.GOODS,
            name="Monitor",
            sku="MON-001",
            unit="PCS",
            hsn_code="8528",
            tax_rate=18,
            purchase_price=10000,
            selling_price=15000,
        )

        cls.deal_a = Deal.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_a.id,
            deal_code="DEAL000001",
            customer_id=cls.customer_a.id,
            title="Laptop Deal",
            description="Laptop sales opportunity",
            stage=Deal.DealStage.PROPOSAL,
            status=Deal.DealStatus.OPEN,
            amount=100000,
            probability=70,
        )

        cls.deal_b = Deal.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_b.id,
            deal_code="DEAL000001",
            customer_id=cls.customer_b.id,
            title="Monitor Deal",
            description="Monitor sales opportunity",
            stage=Deal.DealStage.PROPOSAL,
            status=Deal.DealStatus.OPEN,
            amount=30000,
            probability=50,
        )

        cls.quote_a = Quote.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_a.id,
            quote_code="QUO000001",
            customer_id=cls.customer_a.id,
            deal_id=cls.deal_a.id,
            title="Laptop Quotation",
            notes="Initial quotation",
            status=Quote.QuoteStatus.DRAFT,
            subtotal=100000,
            tax_amount=18000,
            total_amount=118000,
        )

        QuoteItem.objects.using(
            "shared_db"
        ).create(
            quote_id=cls.quote_a.id,
            product_id=cls.product_a.id,
            description="Laptop",
            quantity=Decimal("2"),
            unit_price=Decimal("50000"),
            tax_rate=Decimal("18"),
            line_subtotal=Decimal("100000"),
            line_tax=Decimal("18000"),
            line_total=Decimal("118000"),
        )

        cls.quote_b = Quote.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_b.id,
            quote_code="QUO000001",
            customer_id=cls.customer_b.id,
            deal_id=cls.deal_b.id,
            title="Monitor Quotation",
            notes="Tenant B quotation",
            status=Quote.QuoteStatus.DRAFT,
            subtotal=30000,
            tax_amount=5400,
            total_amount=35400,
        )

    def setUp(self):
        self.client = APIClient()

        self.client.force_authenticate(
            user=self.user_a,
        )

        self.client.defaults[
            "HTTP_X_COMPANY_MOBILE"
        ] = self.tenant_a.company_mobile

    def test_list_quotes(self):
        response = self.client.get(
            "/api/quotes/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(len(response.data["results"]),1,)
        self.assertEqual(response.data["results"][0]["quote_code"],"QUO000001",)

    def test_get_quote_with_items(self):
        response = self.client.get(
            f"/api/quotes/{self.quote_a.id}/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(response.data["data"]["title"],"Laptop Quotation",)
        self.assertEqual(len(response.data["data"]["items"]),1,)
        self.assertEqual(response.data["data"]["items"][0]["product_id"],self.product_a.id,)

    def test_cross_tenant_quote_not_visible(self):
        response = self.client.get(
            f"/api/quotes/{self.quote_b.id}/",
        )

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND,)

    def test_create_quote(self):
        response = self.client.post(
            "/api/quotes/",
            {
                "customer_id": self.customer_a.id,
                "deal_id": self.deal_a.id,
                "title": "New Laptop Quote",
                "notes": "New quotation",
                "items": [
                    {
                        "product_id": self.product_a.id,
                        "quantity": "3",
                        "unit_price": "50000",
                        "tax_rate": "18",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_201_CREATED,)
        self.assertEqual(response.data["data"]["quote_code"],"QUO000002",)
        self.assertEqual(response.data["data"]["subtotal"],"150000.00",)
        self.assertEqual(response.data["data"]["tax_amount"],"27000.00",)
        self.assertEqual(response.data["data"]["total_amount"],"177000.00",)
        self.assertEqual(len(response.data["data"]["items"]),1,)

    def test_create_quote_with_multiple_items(self):
        response = self.client.post(
            "/api/quotes/",
            {
                "customer_id": self.customer_a.id,
                "deal_id": self.deal_a.id,
                "title": "Multiple Product Quote",
                "items": [
                    {
                        "product_id": self.product_a.id,
                        "quantity": "2",
                        "unit_price": "50000",
                        "tax_rate": "18",
                    },
                    {
                        "product_id": self.product_a.id,
                        "quantity": "1",
                        "unit_price": "25000",
                        "tax_rate": "18",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_201_CREATED,)
        self.assertEqual(response.data["data"]["subtotal"],"125000.00",)
        self.assertEqual(response.data["data"]["tax_amount"],"22500.00",)
        self.assertEqual(response.data["data"]["total_amount"],"147500.00",)
        self.assertEqual(len(response.data["data"]["items"]),2,)

    def test_create_quote_with_other_tenant_customer_fails(self):
        response = self.client.post(
            "/api/quotes/",
            {
                "customer_id": self.customer_b.id,
                "deal_id": None,
                "title": "Invalid Customer Quote",
                "items": [
                    {
                        "product_id": self.product_a.id,
                        "quantity": "1",
                        "unit_price": "50000",
                        "tax_rate": "18",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND,)

    def test_create_quote_with_other_tenant_product_fails(self):
        response = self.client.post(
            "/api/quotes/",
            {
                "customer_id": self.customer_a.id,
                "deal_id": self.deal_a.id,
                "title": "Invalid Product Quote",
                "items": [
                    {
                        "product_id": self.product_b.id,
                        "quantity": "1",
                        "unit_price": "15000",
                        "tax_rate": "18",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND,)

    def test_create_quote_with_other_tenant_deal_fails(self):
        response = self.client.post(
            "/api/quotes/",
            {
                "customer_id": self.customer_a.id,
                "deal_id": self.deal_b.id,
                "title": "Invalid Deal Quote",
                "items": [
                    {
                        "product_id": self.product_a.id,
                        "quantity": "1",
                        "unit_price": "50000",
                        "tax_rate": "18",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND,)

    def test_create_quote_without_items_fails(self):
        response = self.client.post(
            "/api/quotes/",
            {
                "customer_id": self.customer_a.id,
                "deal_id": self.deal_a.id,
                "title": "Empty Quote",
                "items": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

    def test_create_quote_with_zero_quantity_fails(self):
        response = self.client.post(
            "/api/quotes/",
            {
                "customer_id": self.customer_a.id,
                "deal_id": self.deal_a.id,
                "title": "Invalid Quantity Quote",
                "items": [
                    {
                        "product_id": self.product_a.id,
                        "quantity": "0",
                        "unit_price": "50000",
                        "tax_rate": "18",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

    def test_create_quote_with_negative_price_fails(self):
        response = self.client.post(
            "/api/quotes/",
            {
                "customer_id": self.customer_a.id,
                "deal_id": self.deal_a.id,
                "title": "Invalid Price Quote",
                "items": [
                    {
                        "product_id": self.product_a.id,
                        "quantity": "1",
                        "unit_price": "-50000",
                        "tax_rate": "18",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

    def test_search_quotes(self):
        response = self.client.get(
            "/api/quotes/?search=Laptop",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(len(response.data["results"]),1,)
        self.assertEqual(response.data["results"][0]["title"],"Laptop Quotation",)

    def test_filter_quotes_by_status(self):
        response = self.client.get(
            "/api/quotes/?status=DRAFT",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(len(response.data["results"]),1,)
        self.assertEqual(response.data["results"][0]["status"],"DRAFT",)

    def test_mark_quote_as_sent(self):
        response = self.client.post(
            f"/api/quotes/{self.quote_a.id}/sent/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(response.data["data"]["status"],"SENT",)

    def test_accept_quote(self):
        response = self.client.post(
            f"/api/quotes/{self.quote_a.id}/accepted/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(response.data["data"]["status"],"ACCEPTED",)

    def test_accepted_quote_cannot_change_status(self):
        self.client.post(
            f"/api/quotes/{self.quote_a.id}/accepted/",
        )

        response = self.client.post(
            f"/api/quotes/{self.quote_a.id}/rejected/",
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

    def test_expired_quote_cannot_change_status(self):
        self.quote_a.status = Quote.QuoteStatus.EXPIRED

        self.quote_a.save(
            using="shared_db",
            update_fields=["status"],
        )

        response = self.client.post(
            f"/api/quotes/{self.quote_a.id}/sent/",
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

    def test_delete_quote(self):
        response = self.client.delete(
            f"/api/quotes/{self.quote_a.id}/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)

        self.quote_a.refresh_from_db()

        self.assertFalse(self.quote_a.is_active,)

    def test_unauthenticated_user_cannot_access_quotes(self):
        self.client.force_authenticate(
            user=None,
        )

        response = self.client.get(
            "/api/quotes/",
        )

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED,)
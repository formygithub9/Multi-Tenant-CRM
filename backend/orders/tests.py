from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from authorization.models import Permission
from common.models import Sequence
from customers.models import Customer
from products.models import Product
from quotes.models import Quote, QuoteItem
from orders.models import Order, OrderItem
from rbac.models import Membership, Role, RolePermission
from tenants.models import Tenant


class OrderAPITest(TestCase):
    databases = {"default", "shared_db"}

    @classmethod
    def setUpTestData(cls):
        cls.tenant_a = Tenant.objects.using("default").create(
            name="Order Tenant A",
            company_email="ordera@tenant.com",
            company_mobile="9100000301",
            database_alias="shared_db",
        )
        cls.tenant_b = Tenant.objects.using("default").create(
            name="Order Tenant B",
            company_email="orderb@tenant.com",
            company_mobile="9100000302",
            database_alias="shared_db",
        )

        cls.user_a = User.objects.create_user(
            username="order_user_a",
            email="ordera@example.com",
            password="TestPass123!",
        )

        cls.role_a = Role.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            name="Admin",
        )

        permissions = Permission.objects.using("shared_db").filter(
            code__in=[
                "orders.view",
                "orders.create",
                "orders.update",
                "orders.delete",
                "orders.approve",
            ],
            is_active=True,
        )
        RolePermission.objects.using("shared_db").bulk_create([
            RolePermission(role=cls.role_a, permission=permission)
            for permission in permissions
        ])

        Membership.objects.using("shared_db").create(
            user=cls.user_a,
            tenant_id=cls.tenant_a.id,
            role=cls.role_a,
        )

        Sequence.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            sequence_type=Sequence.SequenceType.ORDER,
            next_number=2,
        )

        cls.customer_a = Customer.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            customer_code="CUS000001",
            customer_type="BUSINESS",
            contact_name="Rahul Sharma",
            company_name="ABC Technologies",
            email="rahul@abc.com",
            mobile="9999999999",
        )
        cls.customer_b = Customer.objects.using("shared_db").create(
            tenant_id=cls.tenant_b.id,
            customer_code="CUS000001",
            customer_type="BUSINESS",
            contact_name="Amit Verma",
            company_name="XYZ Technologies",
            email="amit@xyz.com",
            mobile="8888888888",
        )

        cls.product_a = Product.objects.using("shared_db").create(
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
        cls.product_b = Product.objects.using("shared_db").create(
            tenant_id=cls.tenant_b.id,
            product_code="PROD000001",
            product_type=Product.ProductType.GOODS,
            name="Product B",
            sku="PROD-B-001",
            unit="PCS",
            hsn_code="8471",
            tax_rate=18,
            purchase_price=400,
            selling_price=500,
        )

        cls.quote_a = Quote.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            quote_code="QUO000001",
            customer_id=cls.customer_a.id,
            title="Laptop Quote",
            status=Quote.QuoteStatus.ACCEPTED,
            subtotal=Decimal("100000.00"),
            tax_amount=Decimal("18000.00"),
            total_amount=Decimal("118000.00"),
        )
        QuoteItem.objects.using("shared_db").create(
            quote_id=cls.quote_a.id,
            product_id=cls.product_a.id,
            description="Laptop",
            quantity=Decimal("2.00"),
            unit_price=Decimal("50000.00"),
            tax_rate=Decimal("18.00"),
            line_subtotal=Decimal("100000.00"),
            line_tax=Decimal("18000.00"),
            line_total=Decimal("118000.00"),
        )

        cls.quote_b = Quote.objects.using("shared_db").create(
            tenant_id=cls.tenant_b.id,
            quote_code="QUO000001",
            customer_id=cls.customer_b.id,
            title="Tenant B Quote",
            status=Quote.QuoteStatus.ACCEPTED,
            subtotal=Decimal("1000.00"),
            tax_amount=Decimal("180.00"),
            total_amount=Decimal("1180.00"),
        )
        QuoteItem.objects.using("shared_db").create(
            quote_id=cls.quote_b.id,
            product_id=cls.product_b.id,
            description="Product B",
            quantity=Decimal("2.00"),
            unit_price=Decimal("500.00"),
            tax_rate=Decimal("18.00"),
            line_subtotal=Decimal("1000.00"),
            line_tax=Decimal("180.00"),
            line_total=Decimal("1180.00"),
        )

        cls.order_a = Order.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            order_code="ORD000001",
            quote_id=cls.quote_a.id,
            customer_id=cls.customer_a.id,
            status=Order.OrderStatus.DRAFT,
            subtotal=Decimal("100000.00"),
            tax_amount=Decimal("18000.00"),
            total_amount=Decimal("118000.00"),
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user_a)
        self.client.defaults["HTTP_X_COMPANY_MOBILE"] = self.tenant_a.company_mobile

    def test_list_orders(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["order_code"], "ORD000001")

    def test_get_order(self):
        response = self.client.get(f"/api/orders/{self.order_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["order_code"], "ORD000001")

    def test_cross_tenant_order_not_visible(self):
        other_order = Order.objects.using("shared_db").create(
            tenant_id=self.tenant_b.id,
            order_code="ORD000001",
            quote_id=self.quote_b.id,
            customer_id=self.customer_b.id,
            status=Order.OrderStatus.DRAFT,
        )
        response = self.client.get(f"/api/orders/{other_order.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_from_accepted_quote(self):
        quote = Quote.objects.using("shared_db").create(
            tenant_id=self.tenant_a.id,
            quote_code="QUO000003",
            customer_id=self.customer_a.id,
            title="New Laptop Quote",
            status=Quote.QuoteStatus.ACCEPTED,
            subtotal=Decimal("100000.00"),
            tax_amount=Decimal("18000.00"),
            total_amount=Decimal("118000.00"),
        )
        QuoteItem.objects.using("shared_db").create(
            quote_id=quote.id,
            product_id=self.product_a.id,
            description="Laptop",
            quantity=Decimal("2.00"),
            unit_price=Decimal("50000.00"),
            tax_rate=Decimal("18.00"),
            line_subtotal=Decimal("100000.00"),
            line_tax=Decimal("18000.00"),
            line_total=Decimal("118000.00"),
        )

        response = self.client.post(
            "/api/orders/",
            {"quote_id": quote.id, "notes": "Customer confirmed purchase"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["subtotal"], "100000.00")
        self.assertEqual(response.data["data"]["tax_amount"], "18000.00")
        self.assertEqual(response.data["data"]["total_amount"], "118000.00")
        self.assertEqual(len(response.data["data"]["items"]), 1)

    def test_order_cannot_be_created_from_draft_quote(self):
        self.quote_a.status = Quote.QuoteStatus.DRAFT
        self.quote_a.save(using="shared_db", update_fields=["status"])
        response = self.client.post(
            "/api/orders/",
            {"quote_id": self.quote_a.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_cannot_be_created_from_other_tenant_quote(self):
        response = self.client.post(
            "/api/orders/",
            {"quote_id": self.quote_b.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_order_for_quote_is_rejected(self):
        response = self.client.post(
            "/api/orders/",
            {"quote_id": self.quote_a.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_items_copy_quote_pricing(self):
        quote = Quote.objects.using("shared_db").create(
            tenant_id=self.tenant_a.id,
            quote_code="QUO000002",
            customer_id=self.customer_a.id,
            title="Second Laptop Quote",
            status=Quote.QuoteStatus.ACCEPTED,
            subtotal=Decimal("100000.00"),
            tax_amount=Decimal("18000.00"),
            total_amount=Decimal("118000.00"),
        )
        QuoteItem.objects.using("shared_db").create(
            quote_id=quote.id,
            product_id=self.product_a.id,
            description="Laptop",
            quantity=Decimal("2.00"),
            unit_price=Decimal("50000.00"),
            tax_rate=Decimal("18.00"),
            line_subtotal=Decimal("100000.00"),
            line_tax=Decimal("18000.00"),
            line_total=Decimal("118000.00"),
        )
        response = self.client.post("/api/orders/", {"quote_id": quote.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data["data"]["id"]
        item = OrderItem.objects.using("shared_db").get(order_id=order_id)
        self.assertEqual(item.quantity, Decimal("2.00"))
        self.assertEqual(item.unit_price, Decimal("50000.00"))
        self.assertEqual(item.line_total, Decimal("118000.00"))
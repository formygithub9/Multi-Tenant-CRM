from decimal import Decimal

from django.test import TestCase

from common.models import Sequence
from invoices.models import Invoice, InvoiceItem
from invoices.services import InvoiceService
from orders.models import Order, OrderItem
from core.exceptions import BadRequestException


class InvoiceServiceTest(TestCase):
    databases = {"default", "shared_db"}

    @classmethod
    def setUpTestData(cls):
        # Reuse the Tenant, Customer, Product, User, Membership, and Role
        # fixture pattern from orders/tests.py.
        from tenants.models import Tenant
        from customers.models import Customer
        from products.models import Product

        cls.tenant = Tenant.objects.using("default").create(
            name="Invoice Tenant",
            company_email="invoice@tenant.com",
            company_mobile="9100000401",
            database_alias="shared_db",
        )
        cls.customer = Customer.objects.using("shared_db").create(
            tenant_id=cls.tenant.id,
            customer_code="CUS000001",
            customer_type="BUSINESS",
            contact_name="Invoice Customer",
            company_name="Invoice Company",
            email="invoice@example.com",
            mobile="9999990000",
        )
        cls.product = Product.objects.using("shared_db").create(
            tenant_id=cls.tenant.id,
            product_code="PROD000001",
            product_type=Product.ProductType.GOODS,
            name="Laptop",
            sku="INV-LAP-001",
            unit="PCS",
            hsn_code="8471",
            tax_rate=18,
            purchase_price=40000,
            selling_price=50000,
        )
        Sequence.objects.using("shared_db").create(
            tenant_id=cls.tenant.id,
            sequence_type=Sequence.SequenceType.INVOICE,
            next_number=1,
        )
        cls.order = Order.objects.using("shared_db").create(
            tenant_id=cls.tenant.id,
            order_code="ORD000001",
            quote_id=1,
            customer_id=cls.customer.id,
            status=Order.OrderStatus.CONFIRMED,
            subtotal=Decimal("100000.00"),
            tax_amount=Decimal("18000.00"),
            total_amount=Decimal("118000.00"),
        )
        OrderItem.objects.using("shared_db").create(
            order_id=cls.order.id,
            product_id=cls.product.id,
            description="Laptop",
            quantity=Decimal("2.00"),
            unit_price=Decimal("50000.00"),
            tax_rate=Decimal("18.00"),
            line_subtotal=Decimal("100000.00"),
            line_tax=Decimal("18000.00"),
            line_total=Decimal("118000.00"),
        )

    def test_create_invoice_from_confirmed_order(self):
        invoice = InvoiceService.create_from_order(self.tenant.id, self.order.id)
        self.assertEqual(invoice.invoice_code, "INV000001")
        self.assertEqual(invoice.total_amount, Decimal("118000.00"))
        self.assertEqual(invoice.status, Invoice.InvoiceStatus.DRAFT)
        self.assertEqual(InvoiceItem.objects.using("shared_db").filter(invoice_id=invoice.id).count(), 1)

    def test_duplicate_invoice_for_order_is_rejected(self):
        InvoiceService.create_from_order(self.tenant.id, self.order.id)
        with self.assertRaises(BadRequestException):
            InvoiceService.create_from_order(self.tenant.id, self.order.id)

    def test_draft_order_cannot_be_invoiced(self):
        self.order.status = Order.OrderStatus.DRAFT
        self.order.save(using="shared_db", update_fields=["status"])
        with self.assertRaises(BadRequestException):
            InvoiceService.create_from_order(self.tenant.id, self.order.id)

    def test_invoice_status_transitions(self):
        invoice = InvoiceService.create_from_order(self.tenant.id, self.order.id)
        invoice = InvoiceService.update_status(invoice, Invoice.InvoiceStatus.ISSUED)
        self.assertEqual(invoice.status, Invoice.InvoiceStatus.ISSUED)
        invoice = InvoiceService.update_status(invoice, Invoice.InvoiceStatus.PAID)
        self.assertEqual(invoice.status, Invoice.InvoiceStatus.PAID)

    def test_paid_invoice_cannot_be_cancelled(self):
        invoice = InvoiceService.create_from_order(self.tenant.id, self.order.id)
        invoice = InvoiceService.update_status(invoice, Invoice.InvoiceStatus.ISSUED)
        invoice = InvoiceService.update_status(invoice, Invoice.InvoiceStatus.PAID)
        with self.assertRaises(BadRequestException):
            InvoiceService.update_status(invoice, Invoice.InvoiceStatus.CANCELLED)

    def test_only_draft_invoice_can_be_deleted(self):
        invoice = InvoiceService.create_from_order(self.tenant.id, self.order.id)
        InvoiceService.delete_invoice(invoice)
        invoice.refresh_from_db(using="shared_db")
        self.assertFalse(invoice.is_active)
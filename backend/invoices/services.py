from datetime import date, timedelta

from django.db import transaction
from django.db.models import Q

from common.models import Sequence
from common.services import SequenceService
from core.db_context import get_current_database
from core.exceptions import BadRequestException, NotFoundException
from orders.models import Order, OrderItem

from invoices.models import Invoice, InvoiceItem


class InvoiceService:

    @classmethod
    def generate_invoice_code(cls, tenant_id):
        number = SequenceService.get_next_number(
            tenant_id=tenant_id,
            sequence_type=Sequence.SequenceType.INVOICE,
        )
        return f"INV{number:06d}"

    @classmethod
    def create_from_order(cls, tenant_id, order_id, notes="", due_days=30):
        database = get_current_database()

        with transaction.atomic(using=database):
            order = Order.objects.using(database).select_for_update().filter(
                id=order_id,
                tenant_id=tenant_id,
                is_active=True,
            ).first()

            if not order:
                raise NotFoundException("Order not found.")

            if order.status not in {
                Order.OrderStatus.CONFIRMED,
                Order.OrderStatus.COMPLETED,
            }:
                raise BadRequestException(
                    "Invoices can only be created from confirmed or completed orders."
                )

            if Invoice.objects.using(database).filter(
                tenant_id=tenant_id,
                order_id=order.id,
            ).exists():
                raise BadRequestException("An invoice already exists for this order.")

            order_items = list(
                OrderItem.objects.using(database).filter(order_id=order.id).order_by("id")
            )

            if not order_items:
                raise BadRequestException("Cannot create an invoice without order items.")

            invoice = Invoice.objects.using(database).create(
                tenant_id=tenant_id,
                invoice_code=cls.generate_invoice_code(tenant_id),
                order_id=order.id,
                customer_id=order.customer_id,
                status=Invoice.InvoiceStatus.DRAFT,
                due_date=date.today() + timedelta(days=due_days),
                notes=notes,
                subtotal=order.subtotal,
                tax_amount=order.tax_amount,
                total_amount=order.total_amount,
            )

            InvoiceItem.objects.using(database).bulk_create([
                InvoiceItem(
                    invoice_id=invoice.id,
                    product_id=item.product_id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_rate=item.tax_rate,
                    line_subtotal=item.line_subtotal,
                    line_tax=item.line_tax,
                    line_total=item.line_total,
                )
                for item in order_items
            ])

        return invoice

    @classmethod
    def get_invoices(cls, tenant_id, search=None, status=None, customer_id=None):
        database = get_current_database()
        queryset = Invoice.objects.using(database).filter(
            tenant_id=tenant_id,
            is_active=True,
        )

        if search:
            queryset = queryset.filter(
                Q(invoice_code__icontains=search) | Q(notes__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        return queryset.order_by("-id")

    @classmethod
    def get_invoice_by_id(cls, tenant_id, invoice_id):
        database = get_current_database()
        invoice = Invoice.objects.using(database).filter(
            id=invoice_id,
            tenant_id=tenant_id,
            is_active=True,
        ).first()

        if not invoice:
            raise NotFoundException("Invoice not found.")

        return invoice

    @classmethod
    def get_invoice_items(cls, invoice_id):
        database = get_current_database()
        return InvoiceItem.objects.using(database).filter(invoice_id=invoice_id).order_by("id")

    @classmethod
    def update_notes(cls, invoice, notes):
        database = get_current_database()

        if invoice.status != Invoice.InvoiceStatus.DRAFT:
            raise BadRequestException("Only draft invoices can be edited.")

        with transaction.atomic(using=database):
            invoice.notes = notes
            invoice.save(using=database, update_fields=["notes", "updated_at"])

        return invoice

    @classmethod
    def update_status(cls, invoice, new_status):
        database = get_current_database()
        transitions = {
            Invoice.InvoiceStatus.DRAFT: {
                Invoice.InvoiceStatus.ISSUED,
                Invoice.InvoiceStatus.CANCELLED,
            },
            Invoice.InvoiceStatus.ISSUED: {
                Invoice.InvoiceStatus.PAID,
                Invoice.InvoiceStatus.CANCELLED,
            },
            Invoice.InvoiceStatus.PAID: set(),
            Invoice.InvoiceStatus.CANCELLED: set(),
        }

        if new_status not in transitions.get(invoice.status, set()):
            raise BadRequestException(
                f"Cannot change invoice status from {invoice.status} to {new_status}."
            )

        with transaction.atomic(using=database):
            invoice.status = new_status
            if new_status == Invoice.InvoiceStatus.ISSUED and not invoice.invoice_date:
                invoice.invoice_date = date.today()

            invoice.save(using=database, update_fields=["status", "invoice_date", "updated_at"])

        return invoice

    @classmethod
    def delete_invoice(cls, invoice):
        database = get_current_database()

        if invoice.status != Invoice.InvoiceStatus.DRAFT:
            raise BadRequestException("Only draft invoices can be deleted.")

        with transaction.atomic(using=database):
            invoice.is_active = False
            invoice.save(using=database, update_fields=["is_active", "updated_at"])

        return invoice
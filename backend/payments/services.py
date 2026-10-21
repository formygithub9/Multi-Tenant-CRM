
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from common.models import Sequence
from common.services import SequenceService
from core.db_context import get_current_database
from core.exceptions import BadRequestException, NotFoundException
from invoices.models import Invoice
from payments.models import Payment


def _get_invoice(tenant_id, invoice_id, database, lock=False):
    queryset = Invoice.objects.using(database).filter(
        tenant_id=tenant_id,
        id=invoice_id,
        is_active=True,
    )
    if lock:
        queryset = queryset.select_for_update()
    invoice = queryset.first()
    if not invoice:
        raise NotFoundException("Invoice not found.")
    return invoice


def _completed_total(tenant_id, invoice_id, database, exclude_payment_id=None):
    queryset = Payment.objects.using(database).filter(
        tenant_id=tenant_id,
        invoice_id=invoice_id,
        is_active=True,
        status=Payment.PaymentStatus.COMPLETED,
    )
    if exclude_payment_id is not None:
        queryset = queryset.exclude(id=exclude_payment_id)
    total = sum(queryset.values_list("amount", flat=True), Decimal("0.00"))
    return total


class PaymentService:
    @staticmethod
    @transaction.atomic
    def create_payment(tenant_id, invoice_id, amount, payment_method, reference="", notes=""):
        database = get_current_database()
        invoice = _get_invoice(tenant_id, invoice_id, database, lock=True)

        if invoice.status != Invoice.Status.ISSUED:
            raise BadRequestException("Payments can only be recorded for issued invoices.")

        amount = Decimal(str(amount))
        if amount <= 0:
            raise BadRequestException("Payment amount must be greater than zero.")

        outstanding = invoice.total_amount - _completed_total(tenant_id, invoice.id, database)
        if amount > outstanding:
            raise BadRequestException("Payment amount exceeds the invoice's outstanding balance.")

        payment_code = SequenceService.get_next_number(tenant_id, Sequence.SequenceType.PAYMENT)

        payment = Payment.objects.using(database).create(
            tenant_id=tenant_id,
            payment_code=payment_code,
            invoice_id=invoice.id,
            amount=amount,
            payment_method=payment_method,
            status=Payment.PaymentStatus.PENDING,
            reference=reference,
            notes=notes,
        )
        return payment

    @staticmethod
    def get_payments(tenant_id, filters=None):
        database = get_current_database()
        queryset = Payment.objects.using(database).filter(
            tenant_id=tenant_id,
            is_active=True,
        )
        filters = filters or {}
        if filters.get("invoice_id"):
            queryset = queryset.filter(invoice_id=filters["invoice_id"])
        if filters.get("status"):
            queryset = queryset.filter(status=filters["status"])
        return queryset

    @staticmethod
    def get_payment_by_id(tenant_id, payment_id):
        database = get_current_database()
        payment = Payment.objects.using(database).filter(
            tenant_id=tenant_id,
            id=payment_id,
            is_active=True,
        ).first()
        if not payment:
            raise NotFoundException("Payment not found.")
        return payment

    @staticmethod
    @transaction.atomic
    def update_status(tenant_id, payment_id, new_status):
        database = get_current_database()
        payment = Payment.objects.using(database).select_for_update().filter(
            tenant_id=tenant_id,
            id=payment_id,
            is_active=True,
        ).first()
        if not payment:
            raise NotFoundException("Payment not found.")

        allowed_transitions = {
            Payment.PaymentStatus.PENDING: {
                Payment.PaymentStatus.COMPLETED,
                Payment.PaymentStatus.FAILED,
            },
            Payment.PaymentStatus.COMPLETED: {
                Payment.PaymentStatus.REFUNDED,
            },
            Payment.PaymentStatus.FAILED: set(),
            Payment.PaymentStatus.REFUNDED: set(),
        }
        if new_status not in allowed_transitions[payment.status]:
            raise BadRequestException(
                f"Cannot change payment status from {payment.status} to {new_status}."
            )

        invoice = _get_invoice(tenant_id, payment.invoice_id, database, lock=True)

        if new_status == Payment.PaymentStatus.COMPLETED:
            if invoice.status != Invoice.Status.ISSUED:
                raise BadRequestException("The invoice is not open for payment.")
            paid_before = _completed_total(tenant_id, invoice.id, database, exclude_payment_id=payment.id)
            if paid_before + payment.amount > invoice.total_amount:
                raise BadRequestException("Completed payments cannot exceed the invoice total.")

        payment.status = new_status
        if new_status == Payment.PaymentStatus.COMPLETED:
            payment.payment_date = timezone.now()
        elif new_status == Payment.PaymentStatus.REFUNDED:
            payment.payment_date = None
        payment.save(using=database, update_fields=["status", "payment_date", "updated_at"])

        completed_total = _completed_total(tenant_id, invoice.id, database)
        if completed_total >= invoice.total_amount:
            invoice.status = Invoice.Status.PAID
            invoice.save(using=database, update_fields=["status", "updated_at"])
        elif invoice.status == Invoice.Status.PAID:
            invoice.status = Invoice.Status.ISSUED
            invoice.save(using=database, update_fields=["status", "updated_at"])

        return payment

    @staticmethod
    @transaction.atomic
    def delete_payment(tenant_id, payment_id):
        database = get_current_database()
        payment = Payment.objects.using(database).select_for_update().filter(
            tenant_id=tenant_id,
            id=payment_id,
            is_active=True,
        ).first()
        if not payment:
            raise NotFoundException("Payment not found.")
        if payment.status == Payment.PaymentStatus.COMPLETED:
            raise BadRequestException("Completed payments cannot be deleted; record a refund instead.")
        payment.is_active = False
        payment.save(using=database, update_fields=["is_active", "updated_at"])
        return payment

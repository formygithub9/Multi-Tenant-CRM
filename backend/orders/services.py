from django.db import transaction
from django.db.models import Q

from common.models import Sequence
from common.services import SequenceService
from core.db_context import get_current_database
from core.exceptions import BadRequestException, NotFoundException
from quotes.models import Quote, QuoteItem
from orders.models import Order, OrderItem


class OrderService:

    @classmethod
    def generate_order_code(cls, tenant_id):
        number = SequenceService.get_next_number(
            tenant_id=tenant_id,
            sequence_type=Sequence.SequenceType.ORDER,
        )
        return f"ORD{number:06d}"

    @classmethod
    def create_order_from_quote(cls, tenant_id, quote_id, notes=""):
        database = get_current_database()

        with transaction.atomic(using=database):
            quote = (
                Quote.objects.using(database)
                .select_for_update()
                .filter(
                    id=quote_id,
                    tenant_id=tenant_id,
                    is_active=True,
                )
                .first()
            )

            if not quote:
                raise NotFoundException("Quote not found.")

            if quote.status != Quote.QuoteStatus.ACCEPTED:
                raise BadRequestException(
                    "Only accepted quotes can be converted into orders."
                )

            if Order.objects.using(database).filter(
                tenant_id=tenant_id,
                quote_id=quote.id,
            ).exists():
                raise BadRequestException(
                    "An order already exists for this quote."
                )

            quote_items = list(
                QuoteItem.objects.using(database).filter(
                    quote_id=quote.id,
                ).order_by("id")
            )

            if not quote_items:
                raise BadRequestException(
                    "Cannot create an order without quote items."
                )

            order = Order.objects.using(database).create(
                tenant_id=tenant_id,
                order_code=cls.generate_order_code(tenant_id),
                quote_id=quote.id,
                customer_id=quote.customer_id,
                status=Order.OrderStatus.DRAFT,
                notes=notes,
                subtotal=quote.subtotal,
                tax_amount=quote.tax_amount,
                total_amount=quote.total_amount,
            )

            OrderItem.objects.using(database).bulk_create([
                OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_rate=item.tax_rate,
                    line_subtotal=item.line_subtotal,
                    line_tax=item.line_tax,
                    line_total=item.line_total,
                )
                for item in quote_items
            ])

        return order

    @classmethod
    def get_orders(cls, tenant_id, search=None, status=None, customer_id=None):
        database = get_current_database()
        queryset = Order.objects.using(database).filter(
            tenant_id=tenant_id,
            is_active=True,
        )

        if search:
            queryset = queryset.filter(
                Q(order_code__icontains=search)
                | Q(notes__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        return queryset.order_by("-id")

    @classmethod
    def get_order_by_id(cls, tenant_id, order_id):
        database = get_current_database()
        order = Order.objects.using(database).filter(
            id=order_id,
            tenant_id=tenant_id,
            is_active=True,
        ).first()

        if not order:
            raise NotFoundException("Order not found.")

        return order

    @classmethod
    def get_order_items(cls, order_id):
        database = get_current_database()
        return OrderItem.objects.using(database).filter(
            order_id=order_id,
        ).order_by("id")

    @classmethod
    def update_order_notes(cls, order, notes):
        database = get_current_database()

        if order.status != Order.OrderStatus.DRAFT:
            raise BadRequestException(
                "Only draft orders can be edited."
            )

        with transaction.atomic(using=database):
            order.notes = notes
            order.save(using=database, update_fields=["notes", "updated_at"])

        return order

    @classmethod
    def update_status(cls, order, new_status):
        database = get_current_database()

        transitions = {
            Order.OrderStatus.DRAFT: {
                Order.OrderStatus.CONFIRMED,
                Order.OrderStatus.CANCELLED,
            },
            Order.OrderStatus.CONFIRMED: {
                Order.OrderStatus.COMPLETED,
                Order.OrderStatus.CANCELLED,
            },
            Order.OrderStatus.COMPLETED: set(),
            Order.OrderStatus.CANCELLED: set(),
        }

        if new_status not in transitions.get(order.status, set()):
            raise BadRequestException(
                f"Cannot change order status from {order.status} to {new_status}."
            )

        with transaction.atomic(using=database):
            order.status = new_status
            order.save(using=database, update_fields=["status", "updated_at"])

        return order

    @classmethod
    def delete_order(cls, order):
        database = get_current_database()

        if order.status != Order.OrderStatus.DRAFT:
            raise BadRequestException(
                "Only draft orders can be deleted."
            )

        with transaction.atomic(using=database):
            order.is_active = False
            order.save(using=database, update_fields=["is_active", "updated_at"])

        return order
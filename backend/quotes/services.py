from decimal import Decimal

from django.db import transaction
from django.db.models import Q

from common.models import Sequence
from common.services import SequenceService
from core.db_context import get_current_database
from core.exceptions import BadRequestException, NotFoundException
from customers.models import Customer
from deals.models import Deal
from products.models import Product
from quotes.models import Quote, QuoteItem


class QuoteService:

    @classmethod
    def generate_quote_code(cls, tenant_id):
        number = SequenceService.get_next_number(
            tenant_id=tenant_id,
            sequence_type=Sequence.SequenceType.QUOTE,
        )

        return f"QUO{number:06d}"

    @classmethod
    def validate_customer(cls, database, tenant_id, customer_id):
        exists = (
            Customer.objects
            .using(database)
            .filter(
                id=customer_id,
                tenant_id=tenant_id,
                is_active=True,
            )
            .exists()
        )

        if not exists:
            raise NotFoundException("Customer not found.")

    @classmethod
    def validate_deal(cls, database, tenant_id, deal_id):
        if deal_id is None:
            return

        exists = (
            Deal.objects
            .using(database)
            .filter(
                id=deal_id,
                tenant_id=tenant_id,
                is_active=True,
            )
            .exists()
        )

        if not exists:
            raise NotFoundException("Deal not found.")

    @classmethod
    def calculate_item(cls, item):
        quantity = Decimal(str(item["quantity"]))
        unit_price = Decimal(str(item["unit_price"]))
        tax_rate = Decimal(str(item.get("tax_rate", 0)))

        if quantity <= 0:
            raise BadRequestException(
                "Quantity must be greater than zero."
            )

        if unit_price < 0:
            raise BadRequestException(
                "Unit price cannot be negative."
            )

        if tax_rate < 0 or tax_rate > 100:
            raise BadRequestException(
                "Tax rate must be between 0 and 100."
            )

        line_subtotal = quantity * unit_price
        line_tax = line_subtotal * tax_rate / Decimal("100")
        line_total = line_subtotal + line_tax

        return {
            "quantity": quantity,
            "unit_price": unit_price,
            "tax_rate": tax_rate,
            "line_subtotal": line_subtotal,
            "line_tax": line_tax,
            "line_total": line_total,
        }

    @classmethod
    def create_quote(cls, validated_data, items):
        database = get_current_database()

        with transaction.atomic(using=database):
            tenant_id = validated_data["tenant_id"]

            cls.validate_customer(
                database,
                tenant_id,
                validated_data["customer_id"],
            )

            cls.validate_deal(
                database,
                tenant_id,
                validated_data.get("deal_id"),
            )

            quote = Quote.objects.using(database).create(
                quote_code=cls.generate_quote_code(tenant_id),
                **validated_data,
            )

            subtotal = Decimal("0")
            tax_amount = Decimal("0")
            total_amount = Decimal("0")

            for item in items:
                product = (
                    Product.objects
                    .using(database)
                    .filter(
                        id=item["product_id"],
                        tenant_id=tenant_id,
                        is_active=True,
                    )
                    .first()
                )

                if not product:
                    raise NotFoundException(
                        "Product not found."
                    )

                calculated = cls.calculate_item(item)

                QuoteItem.objects.using(database).create(
                    quote_id=quote.id,
                    product_id=product.id,
                    description=item.get(
                        "description",
                        product.name,
                    ),
                    **calculated,
                )

                subtotal += calculated["line_subtotal"]
                tax_amount += calculated["line_tax"]
                total_amount += calculated["line_total"]

            quote.subtotal = subtotal
            quote.tax_amount = tax_amount
            quote.total_amount = total_amount

            quote.save(
                using=database,
                update_fields=[
                    "subtotal",
                    "tax_amount",
                    "total_amount",
                    "updated_at",
                ],
            )

        return quote

    @classmethod
    def get_quotes(
        cls,
        tenant_id,
        search=None,
        status=None,
        customer_id=None,
        deal_id=None,
    ):
        database = get_current_database()

        queryset = Quote.objects.using(database).filter(
            tenant_id=tenant_id,
            is_active=True,
        )

        if search:
            queryset = queryset.filter(
                Q(quote_code__icontains=search)
                | Q(title__icontains=search)
                | Q(notes__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if customer_id:
            queryset = queryset.filter(
                customer_id=customer_id,
            )

        if deal_id:
            queryset = queryset.filter(
                deal_id=deal_id,
            )

        return queryset.order_by("-id")

    @classmethod
    def get_quote_by_id(cls, tenant_id, quote_id):
        database = get_current_database()

        quote = (
            Quote.objects
            .using(database)
            .filter(
                tenant_id=tenant_id,
                id=quote_id,
                is_active=True,
            )
            .first()
        )

        if not quote:
            raise NotFoundException("Quote not found.")

        return quote

    @classmethod
    def get_quote_items(cls, quote_id):
        database = get_current_database()

        return QuoteItem.objects.using(database).filter(
            quote_id=quote_id,
        ).order_by("id")

    @classmethod
    def update_status(cls, quote, new_status):
        database = get_current_database()

        allowed_statuses = {
            Quote.QuoteStatus.DRAFT,
            Quote.QuoteStatus.SENT,
            Quote.QuoteStatus.ACCEPTED,
            Quote.QuoteStatus.REJECTED,
            Quote.QuoteStatus.EXPIRED,
        }

        if new_status not in allowed_statuses:
            raise BadRequestException(
                "Invalid quote status."
            )

        if quote.status == Quote.QuoteStatus.ACCEPTED:
            raise BadRequestException(
                "Accepted quote cannot be changed."
            )

        if quote.status == Quote.QuoteStatus.EXPIRED:
            raise BadRequestException(
                "Expired quote cannot be changed."
            )

        with transaction.atomic(using=database):
            quote.status = new_status

            quote.save(
                using=database,
                update_fields=[
                    "status",
                    "updated_at",
                ],
            )

        return quote

    @classmethod
    def delete_quote(cls, quote):
        database = get_current_database()

        with transaction.atomic(using=database):
            quote.is_active = False

            quote.save(
                using=database,
                update_fields=[
                    "is_active",
                    "updated_at",
                ],
            )

        return quote
from django.db import transaction
from django.db.models import Q

from common.models import Sequence
from common.services import SequenceService
from core.db_context import get_current_database
from core.exceptions import BadRequestException, NotFoundException
from customers.models import Customer
from deals.models import Deal


class DealService:

    @classmethod
    def generate_deal_code(cls, tenant_id):
        number = SequenceService.get_next_number(
            tenant_id=tenant_id,
            sequence_type=Sequence.SequenceType.DEAL,
        )

        return f"DEAL{number:06d}"

    @classmethod
    def create_deal(cls, validated_data):
        database = get_current_database()

        with transaction.atomic(using=database):
            tenant_id = validated_data["tenant_id"]
            customer_id = validated_data["customer_id"]

            customer_exists = (
                Customer.objects
                .using(database)
                .filter(
                    id=customer_id,
                    tenant_id=tenant_id,
                    is_active=True,
                )
                .exists()
            )

            if not customer_exists:
                raise NotFoundException("Customer not found.")

            validated_data["deal_code"] = cls.generate_deal_code(
                tenant_id
            )

            deal = Deal.objects.using(database).create(
                **validated_data
            )

        return deal

    @classmethod
    def get_deals(
        cls,
        tenant_id,
        search=None,
        stage=None,
        status=None,
        customer_id=None,
    ):
        database = get_current_database()

        queryset = Deal.objects.using(database).filter(
            tenant_id=tenant_id,
            is_active=True,
        )

        if search:
            queryset = queryset.filter(
                Q(deal_code__icontains=search)
                | Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        if stage:
            queryset = queryset.filter(stage=stage)

        if status:
            queryset = queryset.filter(status=status)

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        return queryset.order_by("-id")

    @classmethod
    def get_deal_by_id(cls, tenant_id, deal_id):
        database = get_current_database()

        deal = (
            Deal.objects
            .using(database)
            .filter(
                tenant_id=tenant_id,
                id=deal_id,
                is_active=True,
            )
            .first()
        )

        if not deal:
            raise NotFoundException("Deal not found.")

        return deal

    @classmethod
    def update_deal(cls, deal, validated_data):
        database = get_current_database()

        with transaction.atomic(using=database):

            if "customer_id" in validated_data:
                customer_exists = (
                    Customer.objects
                    .using(database)
                    .filter(
                        id=validated_data["customer_id"],
                        tenant_id=deal.tenant_id,
                        is_active=True,
                    )
                    .exists()
                )

                if not customer_exists:
                    raise NotFoundException("Customer not found.")

            for field, value in validated_data.items():
                setattr(deal, field, value)

            deal.save(
                using=database,
                update_fields=[
                    *validated_data.keys(),
                    "updated_at",
                ],
            )

        return deal

    @classmethod
    def delete_deal(cls, deal):
        database = get_current_database()

        with transaction.atomic(using=database):
            deal.is_active = False

            deal.save(
                using=database,
                update_fields=[
                    "is_active",
                    "updated_at",
                ],
            )

        return deal

    @classmethod
    def mark_as_won(cls, deal):
        database = get_current_database()

        if deal.status == Deal.DealStatus.LOST:
            raise BadRequestException(
                "Lost deal cannot be marked as won."
            )

        with transaction.atomic(using=database):
            deal.status = Deal.DealStatus.WON
            deal.stage = Deal.DealStage.WON
            deal.probability = 100

            deal.save(
                using=database,
                update_fields=[
                    "status",
                    "stage",
                    "probability",
                    "updated_at",
                ],
            )

        return deal

    @classmethod
    def mark_as_lost(cls, deal):
        database = get_current_database()

        if deal.status == Deal.DealStatus.WON:
            raise BadRequestException(
                "Won deal cannot be marked as lost."
            )

        with transaction.atomic(using=database):
            deal.status = Deal.DealStatus.LOST
            deal.stage = Deal.DealStage.LOST
            deal.probability = 0

            deal.save(
                using=database,
                update_fields=[
                    "status",
                    "stage",
                    "probability",
                    "updated_at",
                ],
            )

        return deal
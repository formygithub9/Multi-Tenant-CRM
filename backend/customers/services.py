from customers.models import Customer
from django.db import transaction
from common.models import Sequence
from common.services import SequenceService
from core.db_context import get_current_database


class CustomerService:

    @classmethod
    def generate_customer_code(cls, tenant_id):

        number = SequenceService.get_next_number(
            tenant_id=tenant_id,
            sequence_type=Sequence.SequenceType.CUSTOMER,
        )

        return f"CUS{number:06d}"

    @classmethod
    def create_customer(cls, validated_data):

        database = get_current_database()

        with transaction.atomic(using=database):

            tenant_id = validated_data["tenant_id"]

            validated_data["customer_code"] = cls.generate_customer_code(
                tenant_id,
            )

            customer = Customer.objects.create(
                **validated_data,
            )

            return customer
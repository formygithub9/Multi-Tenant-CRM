from customers.models import Customer
from django.db import transaction
from common.models import Sequence
from common.services import SequenceService

class CustomerService:

    @classmethod
    def generate_customer_code(cls, tenant_id):

        number = SequenceService.get_next_number(
            tenant_id=tenant_id,
            sequence_type=Sequence.SequenceType.CUSTOMER,
        )

        return f"CUS{number:06d}"

    @classmethod
    @transaction.atomic
    def create_customer(cls, validated_data):
        pass
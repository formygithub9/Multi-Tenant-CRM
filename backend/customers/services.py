from customers.models import Customer
from django.db import transaction
from common.models import Sequence
from common.services import SequenceService
from core.db_context import get_current_database
from core.exceptions import NotFoundException


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
            validated_data["customer_code"] = cls.generate_customer_code(tenant_id,)
            customer = Customer.objects.create(**validated_data,)

            return customer

    @classmethod
    def get_customers(cls, tenant_id):
        return (Customer.objects.filter(tenant_id=tenant_id,is_active=True,).order_by("-id"))

    @classmethod
    def get_customer_by_id(cls, tenant_id, customer_id):

        customer = Customer.objects.filter(tenant_id=tenant_id,id=customer_id,is_active=True,).first()

        if not customer:
            raise NotFoundException("Customer not found.")

        return customer

    @classmethod
    def update_customer(cls, customer, validated_data):

        database = get_current_database()

        with transaction.atomic(using=database):

            for field, value in validated_data.items():
                setattr(customer, field, value)

            customer.save(
                update_fields=[
                    *validated_data.keys(),
                    "updated_at",
                ]
            )

        return customer

    @classmethod
    def delete_customer(cls, customer):

        database = get_current_database()

        with transaction.atomic(using=database):

            customer.is_active = False
            customer.save(update_fields=["is_active", "updated_at"])

        return customer
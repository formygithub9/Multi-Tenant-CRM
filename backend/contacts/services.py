from django.db import transaction
from core.exceptions import NotFoundException
from core.db_context import get_current_database
from contacts.models import Contact


class ContactService:

    @classmethod
    def create_contact(cls, validated_data):
        database = get_current_database()

        with transaction.atomic(using=database):
            contact = Contact.objects.create(**validated_data,)

        return contact

    @classmethod
    def get_contacts(cls, tenant_id, customer_id=None):
        queryset = Contact.objects.filter(tenant_id=tenant_id,is_active=True,)

        if customer_id is not None:
            queryset = queryset.filter(customer_id=customer_id,)

        return queryset.order_by("-id")

    @classmethod
    def get_contact_by_id(cls, tenant_id, contact_id):
        contact = Contact.objects.filter(tenant_id=tenant_id,id=contact_id,is_active=True,).first()

        if not contact:
            raise NotFoundException(
                "Contact not found.",
            )

        return contact

    @classmethod
    def update_contact(cls, contact, validated_data):
        database = get_current_database()

        with transaction.atomic(using=database):
            for field, value in validated_data.items():
                setattr(contact, field, value)

            contact.save(
                update_fields=[
                    *validated_data.keys(),
                    "updated_at",
                ],
            )

        return contact

    @classmethod
    def delete_contact(cls, contact):
        database = get_current_database()

        with transaction.atomic(using=database):
            contact.is_active = False

            contact.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ],
            )

        return contact
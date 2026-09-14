from django.db import transaction
from core.exceptions import NotFoundException
from core.db_context import get_current_database

from leads.models import Lead
from common.models import Sequence
from common.services import SequenceService

from customers.models import Customer
from contacts.models import Contact
from core.exceptions import BadRequestException, NotFoundException

from customers.services import CustomerService


class LeadService:

    @classmethod
    def generate_lead_code(cls, tenant_id):

        number = SequenceService.get_next_number(
            tenant_id=tenant_id,
            sequence_type=Sequence.SequenceType.LEAD,
        )

        return f"LEAD{number:06d}"

    @classmethod
    def create_lead(cls, validated_data):

        database = get_current_database()

        with transaction.atomic(using=database):

            tenant_id = validated_data["tenant_id"]

            validated_data["lead_code"] = (
                cls.generate_lead_code(tenant_id)
            )

            lead = Lead.objects.create(
                **validated_data,
            )

        return lead

    @classmethod
    def get_leads(cls, tenant_id):

        return Lead.objects.filter(
            tenant_id=tenant_id,
            is_active=True,
        ).order_by("-id")

    @classmethod
    def get_lead_by_id(cls, tenant_id, lead_id):

        lead = Lead.objects.filter(
            tenant_id=tenant_id,
            id=lead_id,
            is_active=True,
        ).first()

        if not lead:
            raise NotFoundException(
                "Lead not found."
            )

        return lead

    @classmethod
    def update_lead(cls, lead, validated_data):

        database = get_current_database()

        with transaction.atomic(using=database):

            for field, value in validated_data.items():
                setattr(lead, field, value)

            lead.save()

        return lead

    @classmethod
    def delete_lead(cls, lead):

        database = get_current_database()

        with transaction.atomic(using=database):

            lead.is_active = False

            lead.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ],
            )

        return lead

    @classmethod
    def convert_lead(cls, tenant_id, lead_id):

        database = get_current_database()

        with transaction.atomic(using=database):

            lead = (
                Lead.objects
                .select_for_update()
                .filter(
                    tenant_id=tenant_id,
                    id=lead_id,
                    is_active=True,
                )
                .first()
            )

            if not lead:
                raise NotFoundException("Lead not found.")

            if lead.status == Lead.LeadStatus.CONVERTED:
                raise BadRequestException(
                    "Lead has already been converted."
                )

            if lead.status != Lead.LeadStatus.QUALIFIED:
                raise BadRequestException(
                    "Only qualified leads can be converted."
                )

            customer = Customer.objects.create(
                tenant_id=tenant_id,
                customer_code=CustomerService.generate_customer_code(tenant_id),
                customer_type=Customer.CustomerType.BUSINESS,
                contact_name=lead.contact_name,
                company_name=lead.company_name,
                email=lead.email,
                mobile=lead.mobile,
                remarks=lead.notes,
            )

            name_parts = lead.contact_name.strip().split(maxsplit=1)

            contact = Contact.objects.create(
                tenant_id=tenant_id,
                customer_id=customer.id,
                first_name=name_parts[0],
                last_name=name_parts[1] if len(name_parts) > 1 else "",
                email=lead.email,
                mobile=lead.mobile,
                is_primary=True,
            )

            lead.status = Lead.LeadStatus.CONVERTED

            lead.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return customer, contact

from django.db import transaction
from core.exceptions import NotFoundException
from core.db_context import get_current_database

from leads.models import Lead
from common.models import Sequence
from common.services import SequenceService


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
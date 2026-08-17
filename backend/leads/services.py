from django.db import transaction

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
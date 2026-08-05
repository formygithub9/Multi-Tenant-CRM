from django.db import transaction
from common.models import Sequence

class SequenceService:
    @classmethod
    @transaction.atomic
    def get_next_number(cls, tenant_id, sequence_type):

        sequence = (
            Sequence.objects
            .select_for_update()
            .filter(tenant_id=tenant_id,sequence_type=sequence_type,).first())

        if not sequence:
            sequence = Sequence.objects.create(tenant_id=tenant_id,sequence_type=sequence_type,next_number=2,)
            return 1

        current_number = sequence.next_number
        sequence.next_number += 1
        sequence.save(update_fields=["next_number"])
        return current_number
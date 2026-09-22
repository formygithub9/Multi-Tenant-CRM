from django.db import transaction

from common.models import Sequence
from core.db_context import get_current_database


class SequenceService:

    @classmethod
    def get_next_number(cls, tenant_id, sequence_type):

        database = get_current_database()

        with transaction.atomic(using=database):

            sequence, _ = (
                Sequence.objects
                .using(database)
                .get_or_create(
                    tenant_id=tenant_id,
                    sequence_type=sequence_type,
                    defaults={
                        "next_number": 2,
                    },
                )
            )

            sequence = (
                Sequence.objects
                .using(database)
                .select_for_update()
                .get(pk=sequence.pk)
            )

            current_number = sequence.next_number

            sequence.next_number += 1

            sequence.save(
                using=database,
                update_fields=[
                    "next_number",
                    "updated_at",
                ],
            )

            return current_number
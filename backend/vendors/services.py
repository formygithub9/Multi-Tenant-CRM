from django.db import transaction
from django.db.models import Q

from common.models import Sequence
from common.services import SequenceService
from core.db_context import get_current_database
from core.exceptions import NotFoundException

from vendors.models import Vendor


class VendorService:

    @classmethod
    def generate_vendor_code(cls, tenant_id):
        number = SequenceService.get_next_number(
            tenant_id=tenant_id,
            sequence_type=Sequence.SequenceType.VENDOR,
        )
        return f"VEN{number:06d}"

    @classmethod
    def create_vendor(cls, validated_data):
        database = get_current_database()

        with transaction.atomic(using=database):
            tenant_id = validated_data["tenant_id"]

            validated_data["vendor_code"] = (
                cls.generate_vendor_code(tenant_id)
            )

            vendor = Vendor.objects.using(database).create(
                **validated_data
            )

        return vendor

    @classmethod
    def get_vendors(cls, tenant_id, search=None):
        database = get_current_database()

        queryset = (
            Vendor.objects.using(database)
            .filter(
                tenant_id=tenant_id,
                is_active=True,
            )
        )

        if search:
            queryset = queryset.filter(
                Q(vendor_code__icontains=search)
                | Q(contact_name__icontains=search)
                | Q(company_name__icontains=search)
                | Q(email__icontains=search)
                | Q(mobile__icontains=search)
            )

        return queryset.order_by("-id")

    @classmethod
    def get_vendor_by_id(cls, tenant_id, vendor_id):
        database = get_current_database()

        vendor = (
            Vendor.objects.using(database)
            .filter(
                tenant_id=tenant_id,
                id=vendor_id,
                is_active=True,
            )
            .first()
        )

        if not vendor:
            raise NotFoundException("Vendor not found.")

        return vendor

    @classmethod
    def update_vendor(cls, vendor, validated_data):
        database = get_current_database()

        with transaction.atomic(using=database):
            for field, value in validated_data.items():
                setattr(vendor, field, value)

            vendor.save(
                using=database,
                update_fields=[
                    *validated_data.keys(),
                    "updated_at",
                ],
            )

        return vendor

    @classmethod
    def delete_vendor(cls, vendor):
        database = get_current_database()

        with transaction.atomic(using=database):
            vendor.is_active = False

            vendor.save(
                using=database,
                update_fields=[
                    "is_active",
                    "updated_at",
                ],
            )

        return vendor
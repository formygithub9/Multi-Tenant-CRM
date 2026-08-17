from django.db import models


class Sequence(models.Model):
    """
    Stores the next sequence number for each tenant and entity.

    Examples:
        CUSTOMER
        VENDOR
        PRODUCT
        SALES_ORDER
    """

    class SequenceType(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        LEAD = "LEAD", "Lead"
        VENDOR = "VENDOR", "Vendor"
        PRODUCT = "PRODUCT", "Product"
        SALES_ORDER = "SALES_ORDER", "Sales Order"
        PURCHASE_ORDER = "PURCHASE_ORDER", "Purchase Order"
        INVOICE = "INVOICE", "Invoice"

    id = models.BigAutoField(primary_key=True)

    tenant_id = models.PositiveBigIntegerField(db_index=True)

    sequence_type = models.CharField(
        max_length=50,
        choices=SequenceType.choices,
    )

    next_number = models.PositiveBigIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sequences"

        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "sequence_type"],
                name="unique_sequence_per_tenant",
            )
        ]

    def __str__(self):
        return f"{self.tenant_id} - {self.sequence_type}"
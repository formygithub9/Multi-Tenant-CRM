from django.db import models


class Invoice(models.Model):
    class InvoiceStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ISSUED = "ISSUED", "Issued"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    tenant_id = models.PositiveBigIntegerField(db_index=True)
    invoice_code = models.CharField(max_length=30)
    order_id = models.PositiveBigIntegerField()
    customer_id = models.PositiveBigIntegerField()
    status = models.CharField(max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT)
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tenant_id", "invoice_code"], name="unique_invoice_code_per_tenant"),
            models.UniqueConstraint(fields=["tenant_id", "order_id"], name="unique_invoice_order_per_tenant"),
        ]
        ordering = ["-id"]

    def __str__(self):
        return self.invoice_code


class InvoiceItem(models.Model):
    invoice_id = models.PositiveBigIntegerField(db_index=True)
    product_id = models.PositiveBigIntegerField()
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    line_tax = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Invoice {self.invoice_id} - {self.description}"
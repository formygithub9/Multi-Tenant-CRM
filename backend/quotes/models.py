from django.db import models


class Quote(models.Model):

    class QuoteStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SENT = "SENT", "Sent"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        EXPIRED = "EXPIRED", "Expired"

    id = models.BigAutoField(primary_key=True)
    tenant_id = models.PositiveBigIntegerField(db_index=True)
    quote_code = models.CharField(max_length=30,db_index=True,)
    customer_id = models.PositiveBigIntegerField(db_index=True,)
    deal_id = models.PositiveBigIntegerField(null=True,blank=True,db_index=True,)
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20,choices=QuoteStatus.choices,default=QuoteStatus.DRAFT,)
    valid_until = models.DateField(null=True,blank=True,)
    subtotal = models.DecimalField(max_digits=15,decimal_places=2,default=0,)
    tax_amount = models.DecimalField(max_digits=15,decimal_places=2,default=0,)
    total_amount = models.DecimalField(max_digits=15,decimal_places=2,default=0,)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quotes"
        ordering = ["-id"]

        indexes = [
            models.Index(fields=["tenant_id", "quote_code"]),
            models.Index(fields=["tenant_id", "customer_id"]),
            models.Index(fields=["tenant_id", "deal_id"]),
            models.Index(fields=["tenant_id", "status"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "quote_code"],
                name="unique_quote_code_per_tenant",
            ),
        ]

    def __str__(self):
        return self.quote_code


class QuoteItem(models.Model):

    id = models.BigAutoField(primary_key=True)
    quote_id = models.PositiveBigIntegerField(db_index=True,)
    product_id = models.PositiveBigIntegerField(db_index=True,)
    description = models.CharField(max_length=255,blank=True,)
    quantity = models.DecimalField(max_digits=15,decimal_places=2,)
    unit_price = models.DecimalField(max_digits=15,decimal_places=2,)
    tax_rate = models.DecimalField(max_digits=5,decimal_places=2,default=0,)
    line_subtotal = models.DecimalField(max_digits=15,decimal_places=2,default=0,)
    line_tax = models.DecimalField(max_digits=15,decimal_places=2,default=0,)
    line_total = models.DecimalField(max_digits=15,decimal_places=2,default=0,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "quote_items"
        ordering = ["id"]

        indexes = [
            models.Index(fields=["quote_id"]),
            models.Index(fields=["product_id"]),
        ]

    def __str__(self):
        return f"{self.quote_id}-{self.product_id}"
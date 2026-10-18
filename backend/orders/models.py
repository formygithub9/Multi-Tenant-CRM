from django.db import models


class Order(models.Model):

    class OrderStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.BigAutoField(primary_key=True)
    tenant_id = models.PositiveBigIntegerField(db_index=True)
    order_code = models.CharField(max_length=30, db_index=True)
    quote_id = models.PositiveBigIntegerField()
    customer_id = models.PositiveBigIntegerField(db_index=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.DRAFT)
    order_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["tenant_id", "order_code"]),
            models.Index(fields=["tenant_id", "customer_id"]),
            models.Index(fields=["tenant_id", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["tenant_id", "order_code"], name="unique_order_code_per_tenant"),
            models.UniqueConstraint(fields=["tenant_id", "quote_id"], name="unique_order_per_quote"),
        ]

    def __str__(self):
        return self.order_code


class OrderItem(models.Model):

    id = models.BigAutoField(primary_key=True)
    order_id = models.PositiveBigIntegerField(db_index=True)
    product_id = models.PositiveBigIntegerField(db_index=True)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    line_tax = models.DecimalField(max_digits=15, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "order_items"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["order_id"]),
            models.Index(fields=["product_id"]),
        ]

    def __str__(self):
        return f"{self.order_id}-{self.product_id}"
from django.db import models


class Product(models.Model):

    class ProductType(models.TextChoices):
        GOODS = "GOODS", "Goods"
        SERVICE = "SERVICE", "Service"

    id = models.BigAutoField(primary_key=True)
    tenant_id = models.PositiveBigIntegerField(db_index=True)
    product_code = models.CharField(max_length=30,db_index=True,)
    product_type = models.CharField(max_length=20,choices=ProductType.choices,default=ProductType.GOODS,)
    name = models.CharField(max_length=255,)
    sku = models.CharField(max_length=100,blank=True,)
    description = models.TextField(blank=True,)
    unit = models.CharField(max_length=50,default="PCS",)
    hsn_code = models.CharField(max_length=20,blank=True,)
    tax_rate = models.DecimalField(max_digits=5,decimal_places=2,default=0,)
    purchase_price = models.DecimalField(max_digits=15,decimal_places=2,default=0,)
    selling_price = models.DecimalField(max_digits=15,decimal_places=2,default=0,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "products"

        ordering = ["-id"]

        indexes = [
            models.Index(
                fields=["tenant_id", "product_code"]
            ),
            models.Index(
                fields=["tenant_id", "name"]
            ),
            models.Index(
                fields=["tenant_id", "sku"]
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "product_code"],
                name="unique_product_code_per_tenant",
            ),
        ]

    def __str__(self):
        return self.product_code
from django.db import models


class Customer(models.Model):
    """
    Represents a customer belonging to a tenant.

    Supports both Individual and Business customers.
    """

    class CustomerType(models.TextChoices):
        INDIVIDUAL = "INDIVIDUAL", "Individual"
        BUSINESS = "BUSINESS", "Business"

    id = models.BigAutoField(primary_key=True)
    tenant_id = models.PositiveBigIntegerField(db_index=True)
    customer_code = models.CharField(max_length=30,db_index=True,)
    customer_type = models.CharField(max_length=20,choices=CustomerType.choices,default=CustomerType.BUSINESS,)
    contact_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255,blank=True,)
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=20,blank=True,)
    gst_number = models.CharField(max_length=20,blank=True,null=True,)
    pan_number = models.CharField(max_length=20,blank=True,null=True,)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100,blank=True,)
    state = models.CharField(max_length=100,blank=True,)
    country = models.CharField(max_length=100,blank=True,)
    pincode = models.CharField(max_length=20,blank=True,)
    remarks = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"

        ordering = ["customer_code"]

        indexes = [
            models.Index(fields=["tenant_id", "customer_code"]),
            models.Index(fields=["tenant_id", "contact_name"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "customer_code"],
                name="unique_customer_code_per_tenant",
            ),

        ]

    def __str__(self):
        return f"{self.customer_code} - {self.contact_name}"
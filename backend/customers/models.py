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
    tenant = models.ForeignKey("tenants.Tenant",on_delete=models.CASCADE,related_name="customers",)
    customer_code = models.CharField(max_length=30)

    customer_type = models.CharField(
        max_length=20,
        choices=CustomerType.choices,
        default=CustomerType.BUSINESS,
    )

    contact_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255,blank=True,)
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=20,blank=True,)
    gst_number = models.CharField(max_length=20,blank=True,)
    pan_number = models.CharField(max_length=20,blank=True,)
    remarks = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"

        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "customer_code"],
                name="unique_customer_code_per_tenant",
            ),
            models.UniqueConstraint(
                fields=["tenant", "gst_number"],
                name="unique_customer_gst_per_tenant",
            ),
        ]

    def __str__(self):
        return f"{self.customer_code} - {self.name}"

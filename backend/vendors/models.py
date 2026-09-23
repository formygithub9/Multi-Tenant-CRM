from django.db import models


class Vendor(models.Model):

    class VendorType(models.TextChoices):
        INDIVIDUAL = "INDIVIDUAL", "Individual"
        BUSINESS = "BUSINESS", "Business"

    id = models.BigAutoField(primary_key=True)
    tenant_id = models.PositiveBigIntegerField(db_index=True)
    vendor_code = models.CharField(max_length=30,db_index=True,)
    vendor_type = models.CharField(max_length=20,choices=VendorType.choices,default=VendorType.BUSINESS,)
    contact_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255,blank=True,)
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=20,blank=True,)
    gst_number = models.CharField(max_length=20,blank=True,)
    pan_number = models.CharField(max_length=20,blank=True,)
    address = models.TextField(blank=True,)
    city = models.CharField(max_length=100,blank=True,)
    state = models.CharField(max_length=100,blank=True,)
    pincode = models.CharField(max_length=10,blank=True,)
    remarks = models.TextField(blank=True,)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendors"

        ordering = ["-id"]

        indexes = [
            models.Index(
                fields=["tenant_id", "vendor_code"]
            ),
            models.Index(
                fields=["tenant_id", "contact_name"]
            ),
            models.Index(
                fields=["tenant_id", "company_name"]
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "vendor_code"],
                name="unique_vendor_code_per_tenant",
            )
        ]

    def __str__(self):
        return self.vendor_code
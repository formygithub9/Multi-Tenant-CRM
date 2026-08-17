from django.db import models


class Lead(models.Model):

    class LeadStatus(models.TextChoices):
        NEW = "NEW", "New"
        CONTACTED = "CONTACTED", "Contacted"
        QUALIFIED = "QUALIFIED", "Qualified"
        LOST = "LOST", "Lost"
        CONVERTED = "CONVERTED", "Converted"

    class LeadSource(models.TextChoices):
        WEBSITE = "WEBSITE", "Website"
        REFERRAL = "REFERRAL", "Referral"
        SOCIAL_MEDIA = "SOCIAL_MEDIA", "Social Media"
        EMAIL = "EMAIL", "Email"
        PHONE = "PHONE", "Phone"
        OTHER = "OTHER", "Other"

    id = models.BigAutoField(primary_key=True,)
    tenant_id = models.PositiveBigIntegerField(db_index=True,)
    lead_code = models.CharField(max_length=30,db_index=True,)
    contact_name = models.CharField(max_length=255,)
    company_name = models.CharField(max_length=255,blank=True,)
    email = models.EmailField(blank=True,)
    mobile = models.CharField(max_length=20,blank=True,)
    source = models.CharField(max_length=30,choices=LeadSource.choices,default=LeadSource.OTHER,)
    status = models.CharField(max_length=20,choices=LeadStatus.choices,default=LeadStatus.NEW,)
    notes = models.TextField(blank=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "leads"
        ordering = ["-id"]

        indexes = [
            models.Index(
                fields=["tenant_id", "lead_code"],
            ),
            models.Index(
                fields=["tenant_id", "status"],
            ),
            models.Index(
                fields=["tenant_id", "contact_name"],
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "lead_code"],
                name="unique_lead_code_per_tenant",
            ),
        ]

    def __str__(self):
        return f"{self.lead_code} - {self.contact_name}"
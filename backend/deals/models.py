from django.db import models


class Deal(models.Model):

    class DealStage(models.TextChoices):
        QUALIFICATION = "QUALIFICATION", "Qualification"
        PROPOSAL = "PROPOSAL", "Proposal"
        NEGOTIATION = "NEGOTIATION", "Negotiation"
        WON = "WON", "Won"
        LOST = "LOST", "Lost"

    class DealStatus(models.TextChoices):
        OPEN = "OPEN", "Open"
        WON = "WON", "Won"
        LOST = "LOST", "Lost"

    id = models.BigAutoField(primary_key=True)
    tenant_id = models.PositiveBigIntegerField(db_index=True)
    deal_code = models.CharField(max_length=30,db_index=True,)
    customer_id = models.PositiveBigIntegerField(db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    stage = models.CharField(max_length=30,choices=DealStage.choices,default=DealStage.QUALIFICATION,)
    status = models.CharField(max_length=20,choices=DealStatus.choices,default=DealStatus.OPEN,)
    amount = models.DecimalField(max_digits=15,decimal_places=2,default=0,)
    expected_close_date = models.DateField(null=True,blank=True,)
    probability = models.DecimalField(max_digits=5,decimal_places=2,default=0,)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "deals"
        ordering = ["-id"]

        indexes = [
            models.Index(fields=["tenant_id", "deal_code"]),
            models.Index(fields=["tenant_id", "customer_id"]),
            models.Index(fields=["tenant_id", "stage"]),
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "title"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "deal_code"],
                name="unique_deal_code_per_tenant",
            ),
        ]

    def __str__(self):
        return self.deal_code
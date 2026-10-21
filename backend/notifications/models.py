from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        TASK_ASSIGNED = "TASK_ASSIGNED", "Task Assigned"
        TASK_DUE = "TASK_DUE", "Task Due"
        DEAL_UPDATED = "DEAL_UPDATED", "Deal Updated"
        INVOICE_ISSUED = "INVOICE_ISSUED", "Invoice Issued"
        PAYMENT_RECEIVED = "PAYMENT_RECEIVED", "Payment Received"
        SYSTEM = "SYSTEM", "System"

    tenant_id = models.PositiveBigIntegerField(db_index=True)
    recipient_id = models.PositiveBigIntegerField(db_index=True)
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_type = models.CharField(max_length=50, blank=True)
    related_id = models.PositiveBigIntegerField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "recipient_id", "read_at"]),
            models.Index(fields=["tenant_id", "recipient_id", "created_at"]),
        ]

    def __str__(self):
        return self.title
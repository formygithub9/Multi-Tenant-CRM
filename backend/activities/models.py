
from django.conf import settings
from django.db import models


class Activity(models.Model):
    class ActivityType(models.TextChoices):
        TASK = "TASK", "Task"
        CALL = "CALL", "Call"
        MEETING = "MEETING", "Meeting"
        EMAIL = "EMAIL", "Email"
        NOTE = "NOTE", "Note"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    class RelatedType(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        CONTACT = "CONTACT", "Contact"
        LEAD = "LEAD", "Lead"
        DEAL = "DEAL", "Deal"

    tenant_id = models.PositiveBigIntegerField(db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices, default=ActivityType.TASK)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    related_type = models.CharField(max_length=20, choices=RelatedType.choices, null=True, blank=True)
    related_id = models.PositiveBigIntegerField(null=True, blank=True, db_index=True)

    assigned_to_id = models.PositiveBigIntegerField(null=True, blank=True, db_index=True)
    created_by_id = models.PositiveBigIntegerField(db_index=True)

    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_at", "-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "status", "due_at"]),
            models.Index(fields=["tenant_id", "assigned_to_id", "status"]),
            models.Index(fields=["tenant_id", "related_type", "related_id"]),
        ]

    def __str__(self):
        return self.title

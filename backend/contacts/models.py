from django.db import models

# Create your models here.

class Contact(models.Model):

    id = models.BigAutoField(primary_key=True)
    tenant_id = models.PositiveBigIntegerField(db_index=True,)
    customer_id = models.PositiveBigIntegerField(db_index=True,)
    first_name = models.CharField(max_length=100,)
    last_name = models.CharField(max_length=100,blank=True,)
    designation = models.CharField(max_length=150,blank=True,)
    email = models.EmailField(blank=True,)
    mobile = models.CharField(max_length=20,blank=True,)
    is_primary = models.BooleanField(default=False,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "contacts"
        ordering = ["first_name"]
        indexes = [
            models.Index(
                fields=["tenant_id", "customer_id"],
            ),
            models.Index(
                fields=["tenant_id", "first_name"],
            ),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()
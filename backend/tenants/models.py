from django.db import models
from django.utils.text import slugify


class Tenant(models.Model):
    id = models.BigAutoField(primary_key=True,)
    name = models.CharField(max_length=255,)
    slug = models.SlugField(max_length=255,unique=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "tenants"
        ordering = ["name"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Tenant.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Membership(models.Model):
    """
    Associates a user with a tenant and assigns a role.

    Example:
        Roman -> Basawa -> Admin
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey("accounts.User",on_delete=models.CASCADE,related_name="memberships",)
    tenant = models.ForeignKey("Tenant",on_delete=models.CASCADE,related_name="memberships",)
    role = models.ForeignKey("authorization.Role",on_delete=models.PROTECT,related_name="memberships",)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "memberships"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "tenant"],
                name="unique_user_tenant",
            )
        ]
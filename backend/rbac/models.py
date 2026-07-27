from django.db import models

# Create your models here.
class Role(models.Model):
    """
    Represents a tenant-specific role.

    Examples:
        Admin, Manager, Sales Executive
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    tenant = models.ForeignKey("tenants.Tenant",on_delete=models.CASCADE,related_name="roles",)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name
    
class RolePermission(models.Model):
    """
    Maps a role to its assigned permissions.

    Example:
        Admin -> Customer View
    """
    id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey("Role",on_delete=models.CASCADE,related_name="role_permissions",)
    permission = models.ForeignKey("authorization.Permission",on_delete=models.CASCADE,related_name="role_permissions",)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "role_permissions"

        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_role_permission",
            )
        ]

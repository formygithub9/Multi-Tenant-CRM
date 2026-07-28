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
    tenant_id = models.BigIntegerField(db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "name"],
                name="unique_role_per_tenant",
            )
        ]

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

class Membership(models.Model):
    """
    Associates a user with a tenant and assigns a role.

    Example:
        Roman -> Basawa -> Admin
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey("accounts.User",on_delete=models.CASCADE,related_name="memberships",)
    tenant_id = models.BigIntegerField(db_index=True)
    role = models.ForeignKey("rbac.Role",on_delete=models.PROTECT,related_name="memberships",)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "memberships"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "tenant_id"],
                name="unique_user_tenant",
            )
        ]

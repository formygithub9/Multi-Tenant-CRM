from django.db import models

class PermissionType(models.Model):
    """
    Defines the type of action that can be performed on a resource.

    Examples:
        View, Create, Update, Delete, Download
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permission_types"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
class Resource(models.Model):
    """
    Represents an application resource/module.

    Examples:
        Customer, Vendor, Inventory, Purchase Order
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resources"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
class Permission(models.Model):
    """
    Represents a permission by combining a Resource and a PermissionType.

    Example:
        Customer + View
    """
    id = models.BigAutoField(primary_key=True)
    resource = models.ForeignKey("Resource",on_delete=models.CASCADE,related_name="permissions",)
    permission_type = models.ForeignKey("PermissionType",on_delete=models.CASCADE,related_name="permissions",)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permissions"

        constraints = [
            models.UniqueConstraint(
                fields=["resource", "permission_type"],
                name="unique_resource_permission_type",
            )
        ]

    def __str__(self):
        return f"{self.resource.name}.{self.permission_type.name}"
    
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
    permission = models.ForeignKey("Permission",on_delete=models.CASCADE,related_name="role_permissions",)
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



from django.db import migrations


def seed_order_permissions(apps, schema_editor):
    Module = apps.get_model("authorization", "Module")
    PermissionType = apps.get_model("authorization", "PermissionType")
    Permission = apps.get_model("authorization", "Permission")

    module, _ = Module.objects.get_or_create(
        name="Orders",
        defaults={"description": "Customer sales orders", "is_active": True},
    )

    permission_types = PermissionType.objects.filter(
        name__in=["View", "Create", "Update", "Delete", "Export", "Approve"],
        is_active=True,
    )

    for permission_type in permission_types:
        code = f"orders.{permission_type.name.lower()}"
        Permission.objects.get_or_create(
            module=module,
            permission_type=permission_type,
            defaults={"code": code, "is_active": True},
        )


def reverse_order_permissions(apps, schema_editor):
    Permission = apps.get_model("authorization", "Permission")
    Module = apps.get_model("authorization", "Module")
    Permission.objects.filter(module__name="Orders").delete()
    Module.objects.filter(name="Orders").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("authorization", "0005_seed_quote_permissions"),
    ]

    operations = [
        migrations.RunPython(seed_order_permissions, reverse_order_permissions),
    ]
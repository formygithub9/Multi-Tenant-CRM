from django.db import migrations


DEFAULT_MODULES = (
    "Customers",
    "Leads",
    "Vendors",
    "Products",
    "Orders",
    "Invoices",
    "Inventory",
    "Warehouse",
    "Assets",
    "Employees",
    "Reports",
    "Settings",
)

DEFAULT_PERMISSION_TYPES = (
    "View",
    "Create",
    "Update",
    "Delete",
    "Export",
    "Approve",
)


def seed_default_permissions(apps, schema_editor):
    Module = apps.get_model("authorization", "Module")
    PermissionType = apps.get_model("authorization", "PermissionType")
    Permission = apps.get_model("authorization", "Permission")

    modules = {}

    for module_name in DEFAULT_MODULES:
        module, _ = Module.objects.get_or_create(
            name=module_name,
        )
        modules[module_name] = module

    permission_types = {}

    for permission_name in DEFAULT_PERMISSION_TYPES:
        permission_type, _ = PermissionType.objects.get_or_create(
            name=permission_name,
        )
        permission_types[permission_name] = permission_type

    for module in modules.values():
        for permission_type in permission_types.values():
            code = (
                f"{module.name.lower()}."
                f"{permission_type.name.lower()}"
            )

            Permission.objects.get_or_create(
                module=module,
                permission_type=permission_type,
                defaults={
                    "code": code,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ("authorization", "0002_rename_resource_module_and_more"),
    ]

    operations = [
        migrations.RunPython(
            seed_default_permissions,
            migrations.RunPython.noop,
        ),
    ]
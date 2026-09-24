from django.db import migrations


def seed_deal_permissions(apps, schema_editor):
    Module = apps.get_model("authorization", "Module")
    PermissionType = apps.get_model("authorization", "PermissionType")
    Permission = apps.get_model("authorization", "Permission")

    module, _ = Module.objects.get_or_create(
        name="Deals",
        defaults={
            "description": "Sales opportunities and deals",
            "is_active": True,
        },
    )

    permission_types = PermissionType.objects.filter(
        name__in=[
            "View",
            "Create",
            "Update",
            "Delete",
            "Export",
            "Approve",
        ],
        is_active=True,
    )

    for permission_type in permission_types:
        code = (
            f"{module.name.lower()}."
            f"{permission_type.name.lower()}"
        )

        Permission.objects.get_or_create(
            module=module,
            permission_type=permission_type,
            defaults={
                "code": code,
                "is_active": True,
            },
        )


def reverse_deal_permissions(apps, schema_editor):
    Permission = apps.get_model("authorization", "Permission")
    Module = apps.get_model("authorization", "Module")

    Permission.objects.filter(
        module__name="Deals",
    ).delete()

    Module.objects.filter(
        name="Deals",
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("authorization", "0003_seed_default_permissions"),
    ]

    operations = [
        migrations.RunPython(
            seed_deal_permissions,
            reverse_deal_permissions,
        ),
    ]
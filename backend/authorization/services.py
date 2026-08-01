from authorization.models import Module, PermissionType, Permission

class AuthorizationService:
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

    @classmethod
    def create_default_modules(cls):

        modules = {}

        for module_name in cls.DEFAULT_MODULES:

            module, _ = Module.objects.get_or_create(
                name=module_name,
            )

            modules[module_name] = module

        return modules

    DEFAULT_PERMISSION_TYPES = (
        "View",
        "Create",
        "Update",
        "Delete",
        "Export",
        "Approve",
    )

    @classmethod
    def create_default_permission_types(cls):

        permission_types = {}

        for permission_name in cls.DEFAULT_PERMISSION_TYPES:

            permission_type, _ = PermissionType.objects.get_or_create(
                name=permission_name,
            )

            permission_types[permission_name] = permission_type

        return permission_types

    @classmethod
    def create_default_permissions(cls):

        modules = cls.create_default_modules()
        permission_types = cls.create_default_permission_types()

        permissions = {}

        for module in modules.values():

            for permission_type in permission_types.values():

                code = f"{module.name.lower()}.{permission_type.name.lower()}"

                permission, _ = Permission.objects.get_or_create(
                    module=module,
                    permission_type=permission_type,
                    defaults={
                        "code": code,
                    },
                )

                permissions[code] = permission

        return permissions
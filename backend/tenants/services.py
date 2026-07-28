from tenants.models import Tenant


class TenantService:

    @staticmethod
    def get_tenant_by_company_mobile(company_mobile: str):
        return Tenant.objects.using("default").filter(
            company_mobile=company_mobile,
            is_active=True,
        ).first()

    @staticmethod
    def get_database_alias(company_mobile: str):
        tenant = TenantService.get_tenant_by_company_mobile(company_mobile)
        if tenant:
            return tenant.database_alias
        return None
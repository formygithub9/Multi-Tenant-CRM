from tenants.models import Tenant
from core.exceptions import BadRequestException

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

    @staticmethod
    def create_tenant(company_name,company_mobile,company_email,database_alias="shared_db",):
        if Tenant.objects.filter(company_mobile=company_mobile).exists():
            raise BadRequestException("Company mobile already exists.")

        if Tenant.objects.filter(company_email=company_email).exists():
            raise BadRequestException("Company email already exists.")

        return Tenant.objects.create(name=company_name,company_mobile=company_mobile,company_email=company_email,database_alias=database_alias,)
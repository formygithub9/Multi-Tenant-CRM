from core.db_context import (
    clear_current_database,
    set_current_database,
)
from tenants.services import TenantService


class TenantMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        company_mobile = request.headers.get("X-Company-Mobile")

        request.tenant = None
        request.tenant_id = None

        if company_mobile:
            tenant = TenantService.get_tenant_by_company_mobile(
                company_mobile
            )

            if tenant:
                request.tenant = tenant
                request.tenant_id = tenant.id
                set_current_database(tenant.database_alias)

        try:
            response = self.get_response(request)
            return response

        finally:
            clear_current_database()
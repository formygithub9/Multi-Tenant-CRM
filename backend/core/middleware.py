from core.db_context import (set_current_database,clear_current_database,)
from tenants.services import TenantService

class TenantMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        company_mobile = request.headers.get("X-Company-Mobile")

        if company_mobile:
            database_alias = TenantService.get_database_alias(company_mobile)

            if database_alias:
                set_current_database(database_alias)

        try:
            response = self.get_response(request)
            return response
        finally:
            clear_current_database()
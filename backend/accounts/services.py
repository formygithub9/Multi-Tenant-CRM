from tenants.services import TenantService
from core.db_context import set_current_database
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from core.exceptions import BadRequestException, ForbiddenException

from django.db import transaction

from tenants.models import Tenant
from rbac.services import RoleService

class AuthenticationService:

    @staticmethod
    def login(company_mobile, email, password):

        tenant = TenantService.get_tenant_by_company_mobile(company_mobile)
        if not tenant:
            raise BadRequestException("Invalid company mobile.")
        set_current_database(tenant.database_alias)

        user = User.objects.filter(email=email).first()
        if not user:
            raise BadRequestException("Invalid email.")
        if not user.check_password(password):
            raise BadRequestException("Invalid password.")
        if not user.is_active:
            raise ForbiddenException("User account is inactive.")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "tokens": {
                "access": access_token,
                "refresh": refresh_token,
            },
        }

class AuthenticationService:

    ...

    @classmethod
    @transaction.atomic
    def signup(cls,company_name,company_mobile,company_email,username,email,password,):
        pass
from tenants.services import TenantService
from core.db_context import set_current_database
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from core.exceptions import BadRequestException, ForbiddenException
from rbac.services import MembershipService

from django.db import transaction

from tenants.models import Tenant
from rbac.services import RoleService

class AuthenticationService:

    @classmethod
    def generate_tokens(cls,user):

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    
    @classmethod
    def login(cls,company_mobile,email,password):

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

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "tokens": cls.generate_tokens(user),
        }

class AuthenticationService:

    @classmethod
    @transaction.atomic
    def signup(cls,company_name,company_mobile,company_email,username,email,password,):
        tenant = Tenant.objects.create(
            name=company_name,
            company_mobile=company_mobile,
            company_email=company_email,
            database_alias="shared_db",
        )
        roles = RoleService.create_default_roles(tenant)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        MembershipService.create_membership(
            user=user,
            tenant=tenant,
            role=roles["Admin"],
        )
        return {
            "tenant": {
                "id": tenant.id,
                "name": tenant.name,
                "company_mobile": tenant.company_mobile,
                "company_email": tenant.company_email,
            },
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "tokens": cls.generate_tokens(user),
        }
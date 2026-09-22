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
    def login(cls, company_mobile, email, password):

        tenant = TenantService.get_tenant_by_company_mobile(company_mobile)

        if not tenant:
            raise BadRequestException("Invalid company mobile.")
        set_current_database(tenant.database_alias)

        user = (User.objects.filter(email=email,is_active=True,).first())

        if not user:
            raise BadRequestException("Invalid email or password.")

        if not user.check_password(password):
            raise BadRequestException("Invalid email or password.")

        membership = (MembershipService.get_active_membership(user=user,tenant_id=tenant.id,))

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "tenant": {
                "id": tenant.id,
                "name": tenant.name,
                "company_mobile": tenant.company_mobile,
            },
            "role": {
                "id": membership.role.id,
                "name": membership.role.name,
            },
            "tokens": cls.generate_tokens(user),
        }

    @classmethod
    @transaction.atomic
    def signup(cls,company_name,company_mobile,company_email,username,email,password,):
        if User.objects.filter(username=username).exists():
                    raise BadRequestException("Username already exists.")
        
        if User.objects.filter(email=email).exists():
            raise BadRequestException("Email already exists.")
        
        tenant = TenantService.create_tenant(
            company_name=company_name,
            company_mobile=company_mobile,
            company_email=company_email,
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
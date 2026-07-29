from tenants.services import TenantService
from core.db_context import set_current_database
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class AuthenticationService:

    @staticmethod
    def login(company_mobile, email, password):

        tenant = TenantService.get_tenant_by_company_mobile(company_mobile)
        if not tenant:
            raise Exception("Invalid company mobile.")
        set_current_database(tenant.database_alias)

        user = User.objects.filter(email=email).first()
        if not user:
            raise Exception("Invalid email.")
        if not user.check_password(password):
            raise Exception("Invalid password.")
        if not user.is_active:
            raise Exception("User account is inactive.")

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
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from core.responses import APIResponse
from .serializers import LoginSerializer, SignupSerializer
from .services import AuthenticationService


def _set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key=settings.JWT_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
        httponly=True,
        secure=settings.JWT_REFRESH_COOKIE_SECURE,
        samesite=settings.JWT_REFRESH_COOKIE_SAMESITE,
        path=settings.JWT_REFRESH_COOKIE_PATH,
    )
    return response


def _delete_refresh_cookie(response):
    response.delete_cookie(
        key=settings.JWT_REFRESH_COOKIE_NAME,
        path=settings.JWT_REFRESH_COOKIE_PATH,
        samesite=settings.JWT_REFRESH_COOKIE_SAMESITE,
    )
    return response


def _remove_refresh_token_from_response(auth_data):
    data = dict(auth_data)
    tokens = data.pop("tokens", {}) or {}
    data["tokens"] = {"access": tokens.get("access")}
    return data, tokens.get("refresh")


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {"detail": "CSRF cookie set."},
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_protect, name="dispatch")
class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_data = AuthenticationService.login(**serializer.validated_data)
        response_data, refresh_token = _remove_refresh_token_from_response(auth_data)

        response = APIResponse.success(
            message="Login successful.",
            data=response_data,
        )

        return _set_refresh_cookie(response, refresh_token)


@method_decorator(csrf_protect, name="dispatch")
class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_data = AuthenticationService.signup(**serializer.validated_data)
        response_data, refresh_token = _remove_refresh_token_from_response(auth_data)

        response = APIResponse.success(
            message="Account created successfully.",
            data=response_data,
            status_code=status.HTTP_201_CREATED,
        )

        return _set_refresh_cookie(response, refresh_token)


@method_decorator(csrf_protect, name="dispatch")
class CookieTokenRefreshAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)

        if not refresh_token:
            response = Response(
                {"detail": "Refresh cookie is missing or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            return _delete_refresh_cookie(response)

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError, ValidationError):
            response = Response(
                {"detail": "Refresh cookie is invalid or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            return _delete_refresh_cookie(response)

        token_data = dict(serializer.validated_data)
        rotated_refresh = token_data.pop("refresh", None)

        response = Response(token_data, status=status.HTTP_200_OK)

        if rotated_refresh:
            _set_refresh_cookie(response, rotated_refresh)

        return response


@method_decorator(csrf_protect, name="dispatch")
class LogoutAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except (InvalidToken, TokenError, ValidationError):
                pass

        response = APIResponse.success(message="Logged out successfully.")
        return _delete_refresh_cookie(response)
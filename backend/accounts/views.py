from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import SignupSerializer
from .services import AuthenticationService
from core.responses import APIResponse

from .serializers import LoginSerializer


class LoginAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = AuthenticationService.login(**serializer.validated_data)

        return APIResponse.success(message="Login successful.",data=response,)

class SignupView(APIView):

    permission_classes = []

    def post(self, request):
        try:
            serializer = SignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            response = AuthenticationService.signup(
                **serializer.validated_data
            )

            return APIResponse.success(
                message="Account created successfully.",
                data=response,
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print(type(e))
            print(e)
            raise
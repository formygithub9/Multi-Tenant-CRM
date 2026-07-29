from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
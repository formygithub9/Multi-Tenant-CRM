from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import APIResponse
from customers.serializers import CustomerCreateSerializer


class CustomerCreateAPIView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CustomerCreateSerializer(data=request.data,)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()

        return APIResponse.success(
            message="Customer created successfully.",
            data=CustomerCreateSerializer(customer).data,
            status_code=status.HTTP_201_CREATED,
        )
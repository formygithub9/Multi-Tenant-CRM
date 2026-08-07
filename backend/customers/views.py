from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .services import CustomerService
from rbac.models import Membership
from core.responses import APIResponse
from customers.serializers import *
from core.pagination import StandardPagination


class CustomerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id=None):

        membership = Membership.objects.get(user=request.user,)

        if customer_id is not None:
            queryset = CustomerService.get_customer_by_id(tenant_id=membership.tenant_id,customer_id=customer_id)
            serializer = CustomerListSerializer(queryset)
            return APIResponse.success(message="Customer fetched successfully.",data=serializer.data,)

        else:
            queryset = CustomerService.get_customers(tenant_id=membership.tenant_id,)

            paginator = StandardPagination()
            page = paginator.paginate_queryset(queryset,request,)

            serializer = CustomerListSerializer(page,many=True,)

            return paginator.get_paginated_response(serializer.data,)

    def post(self, request):
            serializer = CustomerCreateSerializer(data=request.data,)
            serializer.is_valid(raise_exception=True)
            customer = serializer.save()
    
            return APIResponse.success(
                message="Customer created successfully.",
                data=CustomerCreateSerializer(customer).data,
                status_code=status.HTTP_201_CREATED,
            )
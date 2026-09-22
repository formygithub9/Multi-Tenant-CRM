from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.pagination import StandardPagination
from core.responses import APIResponse

from customers.serializers import (
    CustomerCreateSerializer,
    CustomerListSerializer,
    CustomerUpdateSerializer,
)
from customers.services import CustomerService

from rbac.permissions import HasPermission
from rbac.services import MembershipService


class CustomerAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    required_permissions = {
        "GET": "customers.view",
        "POST": "customers.create",
        "PATCH": "customers.update",
        "DELETE": "customers.delete",
    }

    def get(self, request, customer_id=None):

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        if customer_id is not None:

            customer = CustomerService.get_customer_by_id(
                tenant_id=membership.tenant_id,
                customer_id=customer_id,
            )

            serializer = CustomerListSerializer(customer)

            return APIResponse.success(
                message="Customer fetched successfully.",
                data=serializer.data,
            )

        queryset = CustomerService.get_customers(
            tenant_id=membership.tenant_id,
        )

        paginator = StandardPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
        )

        serializer = CustomerListSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data,
        )

    def post(self, request, customer_id=None):

        if customer_id is not None:

            return APIResponse.error(
                message=(
                    "POST method is not allowed "
                    "for customer detail."
                ),
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        data = request.data.copy()

        # Never trust tenant_id from the client.
        data["tenant_id"] = membership.tenant_id

        serializer = CustomerCreateSerializer(
            data=data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        customer = serializer.save()

        return APIResponse.success(
            message="Customer created successfully.",
            data=CustomerCreateSerializer(customer).data,
            status_code=status.HTTP_201_CREATED,
        )

    def patch(self, request, customer_id):

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        customer = CustomerService.get_customer_by_id(
            tenant_id=membership.tenant_id,
            customer_id=customer_id,
        )

        serializer = CustomerUpdateSerializer(
            customer,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        customer = CustomerService.update_customer(
            customer=customer,
            validated_data=serializer.validated_data,
        )

        return APIResponse.success(
            message="Customer updated successfully.",
            data=CustomerListSerializer(customer).data,
        )

    def delete(self, request, customer_id):

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        customer = CustomerService.get_customer_by_id(
            tenant_id=membership.tenant_id,
            customer_id=customer_id,
        )

        CustomerService.delete_customer(
            customer
        )

        return APIResponse.success(
            message="Customer deleted successfully.",
        )
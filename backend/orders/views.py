from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.pagination import StandardPagination
from core.responses import APIResponse
from orders.serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderUpdateSerializer,
)
from orders.services import OrderService
from rbac.permissions import HasPermission
from rbac.services import MembershipService


class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]

    required_permissions = {
        "GET": "orders.view",
        "POST": "orders.create",
        "PATCH": "orders.update",
        "DELETE": "orders.delete",
    }

    def post(self, request, order_id=None):
        if order_id is not None:
            return APIResponse.error(
                message="POST method is not allowed for order detail.",
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        serializer = OrderCreateSerializer(
            data=request.data,
            context={"tenant_id": membership.tenant_id},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return APIResponse.success(
            message="Order created successfully.",
            data=OrderDetailSerializer(order).data,
            status_code=status.HTTP_201_CREATED,
        )

    def get(self, request, order_id=None):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        if order_id is not None:
            order = OrderService.get_order_by_id(
                tenant_id=membership.tenant_id,
                order_id=order_id,
            )
            return APIResponse.success(
                message="Order fetched successfully.",
                data=OrderDetailSerializer(order).data,
            )

        queryset = OrderService.get_orders(
            tenant_id=membership.tenant_id,
            search=request.query_params.get("search"),
            status=request.query_params.get("status"),
            customer_id=request.query_params.get("customer_id"),
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)

        return paginator.get_paginated_response(
            OrderListSerializer(page, many=True).data,
        )

    def patch(self, request, order_id):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )
        order = OrderService.get_order_by_id(
            tenant_id=membership.tenant_id,
            order_id=order_id,
        )

        serializer = OrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = OrderService.update_order_notes(
            order,
            serializer.validated_data["notes"],
        )

        return APIResponse.success(
            message="Order updated successfully.",
            data=OrderDetailSerializer(order).data,
        )

    def delete(self, request, order_id):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )
        order = OrderService.get_order_by_id(
            tenant_id=membership.tenant_id,
            order_id=order_id,
        )

        OrderService.delete_order(order)

        return APIResponse.success(message="Order deleted successfully.")


class OrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]

    required_permissions = {
        "POST": "orders.approve",
    }

    def post(self, request, order_id, new_status):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )
        order = OrderService.get_order_by_id(
            tenant_id=membership.tenant_id,
            order_id=order_id,
        )

        order = OrderService.update_status(order, new_status.upper())

        return APIResponse.success(
            message="Order status updated successfully.",
            data=OrderDetailSerializer(order).data,
        )
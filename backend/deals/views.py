from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.pagination import StandardPagination
from core.responses import APIResponse
from deals.serializers import (
    DealCreateSerializer,
    DealListSerializer,
    DealUpdateSerializer,
)
from deals.services import DealService
from rbac.permissions import HasPermission
from rbac.services import MembershipService


class DealAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    required_permissions = {
        "GET": "deals.view",
        "POST": "deals.create",
        "PATCH": "deals.update",
        "DELETE": "deals.delete",
    }

    def post(self, request, deal_id=None):
        if deal_id is not None:
            return APIResponse.error(
                message="POST method is not allowed for deal detail.",
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        data = request.data.copy()
        data["tenant_id"] = membership.tenant_id

        serializer = DealCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        deal = serializer.save()

        return APIResponse.success(
            message="Deal created successfully.",
            data=DealListSerializer(deal).data,
            status_code=status.HTTP_201_CREATED,
        )

    def get(self, request, deal_id=None):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        if deal_id is not None:
            deal = DealService.get_deal_by_id(
                tenant_id=membership.tenant_id,
                deal_id=deal_id,
            )

            return APIResponse.success(
                message="Deal fetched successfully.",
                data=DealListSerializer(deal).data,
            )

        search = request.query_params.get("search")
        stage = request.query_params.get("stage")
        deal_status = request.query_params.get("status")
        customer_id = request.query_params.get("customer_id")

        queryset = DealService.get_deals(
            tenant_id=membership.tenant_id,
            search=search,
            stage=stage,
            status=deal_status,
            customer_id=customer_id,
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset,request,)
        serializer = DealListSerializer(page,many=True,)

        return paginator.get_paginated_response(
            serializer.data
        )

    def patch(self, request, deal_id):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        deal = DealService.get_deal_by_id(
            tenant_id=membership.tenant_id,
            deal_id=deal_id,
        )

        serializer = DealUpdateSerializer(
            deal,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        deal = DealService.update_deal(deal=deal,validated_data=serializer.validated_data,)

        return APIResponse.success(
            message="Deal updated successfully.",
            data=DealListSerializer(deal).data,
        )

    def delete(self, request, deal_id):

        membership = MembershipService.get_active_membership(user=request.user,tenant_id=request.tenant_id,)
        deal = DealService.get_deal_by_id(tenant_id=membership.tenant_id,deal_id=deal_id,)
        DealService.delete_deal(deal)

        return APIResponse.success(message="Deal deleted successfully.",)

class DealActionAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    required_permissions = {
        "POST": "deals.approve",
    }

    def post(self, request, deal_id, action):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        deal = DealService.get_deal_by_id(
            tenant_id=membership.tenant_id,
            deal_id=deal_id,
        )

        if action == "won":
            deal = DealService.mark_as_won(deal)

        elif action == "lost":
            deal = DealService.mark_as_lost(deal)

        else:
            return APIResponse.error(
                message="Invalid deal action.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return APIResponse.success(
            message=f"Deal marked as {action} successfully.",
            data=DealListSerializer(deal).data,
        )
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.pagination import StandardPagination
from core.responses import APIResponse
from quotes.serializers import (
    QuoteCreateSerializer,
    QuoteDetailSerializer,
    QuoteListSerializer,
)
from quotes.services import QuoteService
from rbac.permissions import HasPermission
from rbac.services import MembershipService


class QuoteAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    required_permissions = {
        "GET": "quotes.view",
        "POST": "quotes.create",
        "DELETE": "quotes.delete",
    }

    def post(self, request, quote_id=None):
        if quote_id is not None:
            return APIResponse.error(
                message="POST method is not allowed for quote detail.",
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        data = request.data.copy()
        data["tenant_id"] = membership.tenant_id

        serializer = QuoteCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        quote = serializer.save()

        return APIResponse.success(
            message="Quote created successfully.",
            data=QuoteDetailSerializer(quote).data,
            status_code=status.HTTP_201_CREATED,
        )

    def get(self, request, quote_id=None):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        if quote_id is not None:
            quote = QuoteService.get_quote_by_id(
                tenant_id=membership.tenant_id,
                quote_id=quote_id,
            )

            return APIResponse.success(
                message="Quote fetched successfully.",
                data=QuoteDetailSerializer(quote).data,
            )

        search = request.query_params.get("search")
        quote_status = request.query_params.get("status")
        customer_id = request.query_params.get("customer_id")
        deal_id = request.query_params.get("deal_id")

        queryset = QuoteService.get_quotes(
            tenant_id=membership.tenant_id,
            search=search,
            status=quote_status,
            customer_id=customer_id,
            deal_id=deal_id,
        )

        paginator = StandardPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
        )

        serializer = QuoteListSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data,
        )

    def delete(self, request, quote_id):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        quote = QuoteService.get_quote_by_id(
            tenant_id=membership.tenant_id,
            quote_id=quote_id,
        )

        QuoteService.delete_quote(quote)

        return APIResponse.success(
            message="Quote deleted successfully.",
        )


class QuoteStatusAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    required_permissions = {
        "POST": "quotes.approve",
    }

    def post(self, request, quote_id, new_status):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        quote = QuoteService.get_quote_by_id(
            tenant_id=membership.tenant_id,
            quote_id=quote_id,
        )

        quote = QuoteService.update_status(
            quote,
            new_status.upper(),
        )

        return APIResponse.success(
            message="Quote status updated successfully.",
            data=QuoteDetailSerializer(quote).data,
        )
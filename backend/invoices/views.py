from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rbac.permissions import HasPermission
from core.responses import APIResponse
from invoices.models import Invoice
from invoices.serializers import (
    InvoiceCreateSerializer,
    InvoiceDetailSerializer,
    InvoiceListSerializer,
    InvoiceUpdateSerializer,
)
from invoices.services import InvoiceService


class InvoiceAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]

    def get_required_permission(self, request, *args, **kwargs):
        if request.method == "GET":
            return "invoices.view"
        if request.method == "POST":
            return "invoices.create"
        if request.method == "PATCH":
            return "invoices.update"
        if request.method == "DELETE":
            return "invoices.delete"
        return None

    def get(self, request, invoice_id=None):
        tenant_id = request.tenant.id

        if invoice_id is not None:
            invoice = InvoiceService.get_invoice_by_id(tenant_id, invoice_id)
            return APIResponse.success(
                data=InvoiceDetailSerializer(invoice).data,
                message="Invoice retrieved successfully.",
            )

        queryset = InvoiceService.get_invoices(
            tenant_id=tenant_id,
            search=request.query_params.get("search"),
            status=request.query_params.get("status"),
            customer_id=request.query_params.get("customer_id"),
        )

        from common.pagination import StandardPagination

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = InvoiceListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = InvoiceCreateSerializer(
            data=request.data,
            context={"tenant_id": request.tenant.id},
        )
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()

        return APIResponse.success(
            data=InvoiceDetailSerializer(invoice).data,
            message="Invoice created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def patch(self, request, invoice_id=None):
        if invoice_id is None:
            return APIResponse.error(
                message="Invoice ID is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        invoice = InvoiceService.get_invoice_by_id(request.tenant.id, invoice_id)
        serializer = InvoiceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invoice = InvoiceService.update_notes(invoice, serializer.validated_data["notes"])

        return APIResponse.success(
            data=InvoiceDetailSerializer(invoice).data,
            message="Invoice updated successfully.",
        )

    def delete(self, request, invoice_id=None):
        if invoice_id is None:
            return APIResponse.error(
                message="Invoice ID is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        invoice = InvoiceService.get_invoice_by_id(request.tenant.id, invoice_id)
        InvoiceService.delete_invoice(invoice)

        return APIResponse.success(message="Invoice deleted successfully.")


class InvoiceStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "invoices.approve"

    def post(self, request, invoice_id, new_status):
        invoice = InvoiceService.get_invoice_by_id(request.tenant.id, invoice_id)
        invoice = InvoiceService.update_status(invoice, new_status.upper())

        return APIResponse.success(
            data=InvoiceDetailSerializer(invoice).data,
            message="Invoice status updated successfully.",
        )
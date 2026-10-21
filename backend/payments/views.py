
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.pagination import StandardPagination
from core.responses import APIResponse
from payments.models import Payment
from payments.serializers import (
    PaymentCreateSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentStatusSerializer,
)
from payments.services import PaymentService
from rbac.permissions import HasPermission


class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]

    def get_required_permission(self, request, *args, **kwargs):
        return {
            "GET": "payments.view",
            "HEAD": "payments.view",
            "POST": "payments.create",
            "DELETE": "payments.delete",
        }.get(request.method)

    def get(self, request, payment_id=None):
        tenant_id = request.tenant_id

        if payment_id is not None:
            payment = PaymentService.get_payment_by_id(tenant_id, payment_id)
            return APIResponse.success(PaymentDetailSerializer(payment).data)

        queryset = PaymentService.get_payments(
            tenant_id,
            {
                "invoice_id": request.query_params.get("invoice_id"),
                "status": request.query_params.get("status"),
            },
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PaymentListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        payment = PaymentService.create_payment(
            tenant_id=request.tenant_id,
            invoice_id=data["invoice_id"],
            amount=data["amount"],
            payment_method=data["payment_method"],
            reference=data["reference"],
            notes=data["notes"],
        )
        return APIResponse.success(
            PaymentDetailSerializer(payment).data,
            message="Payment created successfully.",
            status_code=201,
        )

    def delete(self, request, payment_id):
        # self.required_permission = "payments.delete"
        payment = PaymentService.delete_payment(request.tenant_id, payment_id)
        return APIResponse.success(
            {"id": payment.id},
            message="Payment deleted successfully.",
        )


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "payments.approve"

    def patch(self, request, payment_id):
        serializer = PaymentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = PaymentService.update_status(
            request.tenant_id,
            payment_id,
            serializer.validated_data["status"],
        )
        return APIResponse.success(
            PaymentDetailSerializer(payment).data,
            message="Payment status updated successfully.",
        )

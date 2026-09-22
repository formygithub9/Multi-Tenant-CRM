from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from contacts.serializers import ContactListSerializer
from core.pagination import StandardPagination
from core.responses import APIResponse
from customers.serializers import CustomerListSerializer
from leads.serializers import (LeadCreateSerializer,LeadListSerializer,LeadUpdateSerializer,)
from leads.services import LeadService
from rbac.permissions import HasPermission
from rbac.services import MembershipService

class LeadAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    required_permissions = {
        "GET": "leads.view",
        "POST": "leads.create",
        "PATCH": "leads.update",
        "DELETE": "leads.delete",
    }

    def post(self, request, lead_id=None):

        if lead_id is not None:
            return APIResponse.error(
                message="POST method is not allowed for lead detail.",
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )
 
        data = request.data.copy()
        data["tenant_id"] = membership.tenant_id

        serializer = LeadCreateSerializer(
            data=data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        lead = serializer.save()

        return APIResponse.success(
            message="Lead created successfully.",
            data=LeadCreateSerializer(lead).data,
            status_code=status.HTTP_201_CREATED,
        )

    def get(self, request, lead_id=None):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        if lead_id is not None:
            lead = LeadService.get_lead_by_id(
                tenant_id=membership.tenant_id,
                lead_id=lead_id,
            )

            serializer = LeadListSerializer(lead)

            return APIResponse.success(
                message="Lead fetched successfully.",
                data=serializer.data,
            )

        search = request.query_params.get("search")
        lead_status = request.query_params.get("status")

        queryset = LeadService.get_leads(
            tenant_id=membership.tenant_id,
            search=search,
            status=lead_status,
        )

        paginator = StandardPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
        )

        serializer = LeadListSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data,
        )

    def patch(self, request, lead_id):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        lead = LeadService.get_lead_by_id(
            tenant_id=membership.tenant_id,
            lead_id=lead_id,
        )

        serializer = LeadUpdateSerializer(
            lead,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        lead = LeadService.update_lead(
            lead,
            serializer.validated_data,
        )

        return APIResponse.success(
            message="Lead updated successfully.",
            data=LeadListSerializer(lead).data,
        )

    def delete(self, request, lead_id):
        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        lead = LeadService.get_lead_by_id(
            tenant_id=membership.tenant_id,
            lead_id=lead_id,
        )

        LeadService.delete_lead(lead)

        return APIResponse.success(
            message="Lead deleted successfully.",
        )

class LeadConvertAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    required_permissions = {
        "POST": "leads.approve",
    }

    def post(self, request, lead_id):

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        customer, contact = LeadService.convert_lead(
            tenant_id=membership.tenant_id,
            lead_id=lead_id,
        )

        return APIResponse.success(
            message="Lead converted successfully.",
            data={
                "customer": CustomerListSerializer(
                    customer,
                ).data,
                "contact": ContactListSerializer(
                    contact,
                ).data,
            },
            status_code=status.HTTP_200_OK,
        )

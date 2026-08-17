from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rbac.models import Membership
from core.responses import APIResponse

from leads.serializers import *
from .services import LeadService
from core.pagination import StandardPagination

class LeadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        membership = Membership.objects.get(user=request.user,)

        data = request.data.copy()
        data["tenant_id"] = membership.tenant_id

        serializer = LeadCreateSerializer(data=data,)
        serializer.is_valid(raise_exception=True,)

        lead = serializer.save()

        return APIResponse.success(
            message="Lead created successfully.",
            data=LeadCreateSerializer(lead).data,
            status_code=status.HTTP_201_CREATED,
        )

    def get(self, request, lead_id=None):
        membership = Membership.objects.get(user=request.user,)

        if lead_id is not None:

            lead = LeadService.get_lead_by_id(tenant_id=membership.tenant_id,lead_id=lead_id,)
            serializer = LeadListSerializer(lead)

            return APIResponse.success(
                message="Lead fetched successfully.",
                data=serializer.data,
            )

        queryset = LeadService.get_leads(tenant_id=membership.tenant_id,)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset,request,)

        serializer = LeadListSerializer(page,many=True,)

        return paginator.get_paginated_response(
            serializer.data,
        )

    def patch(self, request, lead_id):
        membership = Membership.objects.get(user=request.user,)
        lead = LeadService.get_lead_by_id(tenant_id=membership.tenant_id,lead_id=lead_id,)

        serializer = LeadUpdateSerializer(lead,data=request.data,partial=True,)
        serializer.is_valid(raise_exception=True,)

        lead = LeadService.update_lead(lead,serializer.validated_data,)

        return APIResponse.success(
            message="Lead updated successfully.",
            data=LeadListSerializer(lead).data,
        )

    def delete(self, request, lead_id):
        membership = Membership.objects.get(user=request.user,)

        lead = LeadService.get_lead_by_id(tenant_id=membership.tenant_id,lead_id=lead_id,)
        LeadService.delete_lead(lead)

        return APIResponse.success(
            message="Lead deleted successfully.",
        )
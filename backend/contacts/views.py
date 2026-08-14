from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from rbac.models import Membership
from contacts.serializers import ContactCreateSerializer
from contacts.services import ContactService
from core.responses import APIResponse
from .serializers import *
from core.pagination import StandardPagination

class ContactAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        membership = Membership.objects.get(user=request.user,)
        data = request.data.copy()
        data["tenant_id"] = membership.tenant_id
        serializer = ContactCreateSerializer(data=data,)
        serializer.is_valid(raise_exception=True,)
        contact = ContactService.create_contact(serializer.validated_data,)

        return APIResponse.success(
            message="Contact created successfully.",
            data=ContactCreateSerializer(contact).data,
        )

    def get(self, request, contact_id=None):

        membership = Membership.objects.get(user=request.user,)
        if contact_id is not None:
            contact = ContactService.get_contact_by_id(tenant_id=membership.tenant_id,contact_id=contact_id,)
            serializer = ContactListSerializer(contact,)
            return APIResponse.success(
                message="Contact fetched successfully.",
                data=serializer.data,
            )

        queryset = ContactService.get_contacts(tenant_id=membership.tenant_id,)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset,request,)
        serializer = ContactListSerializer(page,many=True,)

        return paginator.get_paginated_response(
            serializer.data,
        )

    def patch(self, request, contact_id):

        membership = Membership.objects.get(user=request.user,)
        contact = ContactService.get_contact_by_id(tenant_id=membership.tenant_id,contact_id=contact_id,)
        serializer = ContactUpdateSerializer(contact,data=request.data,partial=True,)
        serializer.is_valid(raise_exception=True,)
        contact = ContactService.update_contact(contact=contact,validated_data=serializer.validated_data,)

        return APIResponse.success(
            message="Contact updated successfully.",
            data=ContactListSerializer(contact).data,
        )

    def delete(self, request, contact_id):

        membership = Membership.objects.get(user=request.user,)
        contact = ContactService.get_contact_by_id(tenant_id=membership.tenant_id,contact_id=contact_id,)
        ContactService.delete_contact(contact)

        return APIResponse.success(
            message="Contact deleted successfully.",
        )
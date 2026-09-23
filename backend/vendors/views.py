from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.pagination import StandardPagination
from core.responses import APIResponse

from rbac.permissions import HasPermission
from rbac.services import MembershipService

from vendors.serializers import (
    VendorCreateSerializer,
    VendorListSerializer,
    VendorUpdateSerializer,
)
from vendors.services import VendorService


class VendorAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    required_permissions = {
        "GET": "vendors.view",
        "POST": "vendors.create",
        "PATCH": "vendors.update",
        "DELETE": "vendors.delete",
    }

    def post(self, request, vendor_id=None):

        if vendor_id is not None:
            return APIResponse.error(
                message="POST method is not allowed for vendor detail.",
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        membership = MembershipService.get_active_membership(user=request.user,tenant_id=request.tenant_id,)
        data = request.data.copy()

        # Never trust tenant_id from the client.
        data["tenant_id"] = membership.tenant_id
        serializer = VendorCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        vendor = serializer.save()

        return APIResponse.success(
            message="Vendor created successfully.",
            data=VendorListSerializer(vendor).data,
            status_code=status.HTTP_201_CREATED,
        )

    def get(self, request, vendor_id=None):

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        if vendor_id is not None:

            vendor = VendorService.get_vendor_by_id(tenant_id=membership.tenant_id,vendor_id=vendor_id,)
            serializer = VendorListSerializer(vendor)

            return APIResponse.success(
                message="Vendor fetched successfully.",
                data=serializer.data,
            )

        search = request.query_params.get("search")
        queryset = VendorService.get_vendors(tenant_id=membership.tenant_id,search=search,)

        paginator = StandardPagination()

        page = paginator.paginate_queryset(queryset,request,)
        serializer = VendorListSerializer(page,many=True,)

        return paginator.get_paginated_response(serializer.data)

    def patch(self, request, vendor_id):

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        vendor = VendorService.get_vendor_by_id(
            tenant_id=membership.tenant_id,
            vendor_id=vendor_id,
        )

        serializer = VendorUpdateSerializer(
            vendor,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        vendor = VendorService.update_vendor(
            vendor=vendor,
            validated_data=serializer.validated_data,
        )

        return APIResponse.success(
            message="Vendor updated successfully.",
            data=VendorListSerializer(vendor).data,
        )

    def delete(self, request, vendor_id):

        membership = MembershipService.get_active_membership(
            user=request.user,
            tenant_id=request.tenant_id,
        )

        vendor = VendorService.get_vendor_by_id(
            tenant_id=membership.tenant_id,
            vendor_id=vendor_id,
        )

        VendorService.delete_vendor(vendor)

        return APIResponse.success(
            message="Vendor deleted successfully."
        )
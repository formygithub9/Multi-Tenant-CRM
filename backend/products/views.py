from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.pagination import StandardPagination
from core.responses import APIResponse
from products.serializers import (
    ProductCreateSerializer,
    ProductListSerializer,
    ProductUpdateSerializer,
)
from products.services import ProductService
from rbac.permissions import HasPermission
from rbac.services import MembershipService


class ProductAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    required_permissions = {
        "GET": "products.view",
        "POST": "products.create",
        "PATCH": "products.update",
        "DELETE": "products.delete",
    }

    def post(self, request, product_id=None):

        if product_id is not None:
            return APIResponse.error(
                message=(
                    "POST method is not allowed "
                    "for product detail."
                ),
                status_code=(
                    status.HTTP_405_METHOD_NOT_ALLOWED
                ),
            )

        membership = (
            MembershipService.get_active_membership(
                user=request.user,
                tenant_id=request.tenant_id,
            )
        )

        data = request.data.copy()
        data["tenant_id"] = membership.tenant_id
        serializer = ProductCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        return APIResponse.success(
            message="Product created successfully.",
            data=ProductListSerializer(product).data,
            status_code=status.HTTP_201_CREATED,
        )

    def get(self, request, product_id=None):

        membership = (
            MembershipService.get_active_membership(
                user=request.user,
                tenant_id=request.tenant_id,
            )
        )

        if product_id is not None:

            product = ProductService.get_product_by_id(
                tenant_id=membership.tenant_id,
                product_id=product_id,
            )

            return APIResponse.success(
                message="Product fetched successfully.",
                data=ProductListSerializer(product).data,
            )

        search = request.query_params.get("search")
        product_type = request.query_params.get("product_type")

        queryset = ProductService.get_products(
            tenant_id=membership.tenant_id,
            search=search,
            product_type=product_type,
        )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset,request,)
        serializer = ProductListSerializer(page,many=True,)

        return paginator.get_paginated_response(serializer.data)

    def patch(self, request, product_id):

        membership = (
            MembershipService.get_active_membership(
                user=request.user,
                tenant_id=request.tenant_id,
            )
        )

        product = ProductService.get_product_by_id(tenant_id=membership.tenant_id,product_id=product_id,)
        serializer = ProductUpdateSerializer(product,data=request.data,partial=True,)
        serializer.is_valid(raise_exception=True)
        product = ProductService.update_product(product=product,validated_data=serializer.validated_data,)

        return APIResponse.success(
            message="Product updated successfully.",
            data=ProductListSerializer(product).data,
        )

    def delete(self, request, product_id):

        membership = (
            MembershipService.get_active_membership(
                user=request.user,
                tenant_id=request.tenant_id,
            )
        )

        product = ProductService.get_product_by_id(tenant_id=membership.tenant_id,product_id=product_id,)
        ProductService.delete_product(product)

        return APIResponse.success(
            message="Product deleted successfully."
        )
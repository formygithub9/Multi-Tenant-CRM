from decimal import Decimal

from rest_framework import serializers

from products.models import Product
from products.services import ProductService


class ProductValidationMixin:

    def validate(self, attrs):
        product_type = attrs.get(
            "product_type",
            (
                self.instance.product_type
                if self.instance
                else Product.ProductType.GOODS
            ),
        )

        purchase_price = attrs.get(
            "purchase_price",
            (
                self.instance.purchase_price
                if self.instance
                else Decimal("0")
            ),
        )

        selling_price = attrs.get(
            "selling_price",
            (
                self.instance.selling_price
                if self.instance
                else Decimal("0")
            ),
        )

        tax_rate = attrs.get(
            "tax_rate",
            (
                self.instance.tax_rate
                if self.instance
                else Decimal("0")
            ),
        )

        if purchase_price < 0:
            raise serializers.ValidationError(
                {
                    "purchase_price": (
                        "Purchase price cannot be negative."
                    )
                }
            )

        if selling_price < 0:
            raise serializers.ValidationError(
                {
                    "selling_price": (
                        "Selling price cannot be negative."
                    )
                }
            )

        if tax_rate < 0 or tax_rate > 100:
            raise serializers.ValidationError(
                {
                    "tax_rate": (
                        "Tax rate must be between 0 and 100."
                    )
                }
            )

        if (
            product_type == Product.ProductType.GOODS
            and not attrs.get(
                "unit",
                self.instance.unit
                if self.instance
                else "",
            )
        ):
            raise serializers.ValidationError(
                {
                    "unit": (
                        "Unit is required for goods."
                    )
                }
            )

        return attrs


class ProductCreateSerializer(ProductValidationMixin,serializers.ModelSerializer,):
    tenant_id = serializers.IntegerField(
        write_only=True
    )

    class Meta:
        model = Product

        fields = (
            "tenant_id",
            "product_type",
            "name",
            "sku",
            "description",
            "unit",
            "hsn_code",
            "tax_rate",
            "purchase_price",
            "selling_price",
        )

    def create(self, validated_data):
        return ProductService.create_product(
            validated_data
        )


class ProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product

        fields = (
            "id",
            "product_code",
            "product_type",
            "name",
            "sku",
            "description",
            "unit",
            "hsn_code",
            "tax_rate",
            "purchase_price",
            "selling_price",
            "is_active",
            "created_at",
        )


class ProductUpdateSerializer(ProductValidationMixin,serializers.ModelSerializer,):

    class Meta:
        model = Product

        fields = (
            "product_type",
            "name",
            "sku",
            "description",
            "unit",
            "hsn_code",
            "tax_rate",
            "purchase_price",
            "selling_price",
        )
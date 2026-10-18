from rest_framework import serializers

from orders.models import Order, OrderItem
from orders.services import OrderService


class OrderCreateSerializer(serializers.Serializer):
    quote_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def create(self, validated_data):
        return OrderService.create_order_from_quote(
            tenant_id=self.context["tenant_id"],
            quote_id=validated_data["quote_id"],
            notes=validated_data.get("notes", ""),
        )


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_id",
            "description",
            "quantity",
            "unit_price",
            "tax_rate",
            "line_subtotal",
            "line_tax",
            "line_total",
        )


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "order_code",
            "quote_id",
            "customer_id",
            "status",
            "order_date",
            "notes",
            "subtotal",
            "tax_amount",
            "total_amount",
            "created_at",
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "order_code",
            "quote_id",
            "customer_id",
            "status",
            "order_date",
            "notes",
            "subtotal",
            "tax_amount",
            "total_amount",
            "is_active",
            "created_at",
            "items",
        )

    def get_items(self, obj):
        return OrderItemSerializer(
            OrderService.get_order_items(obj.id),
            many=True,
        ).data


class OrderUpdateSerializer(serializers.Serializer):
    notes = serializers.CharField(allow_blank=True)
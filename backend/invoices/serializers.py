from rest_framework import serializers

from invoices.models import Invoice, InvoiceItem
from invoices.services import InvoiceService


class InvoiceCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    due_days = serializers.IntegerField(required=False, min_value=0, max_value=365, default=30)

    def create(self, validated_data):
        return InvoiceService.create_from_order(
            tenant_id=self.context["tenant_id"],
            order_id=validated_data["order_id"],
            notes=validated_data["notes"],
            due_days=validated_data["due_days"],
        )


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "product_id",
            "description",
            "quantity",
            "unit_price",
            "tax_rate",
            "line_subtotal",
            "line_tax",
            "line_total",
        ]
        read_only_fields = fields


class InvoiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_code",
            "order_id",
            "customer_id",
            "status",
            "invoice_date",
            "due_date",
            "subtotal",
            "tax_amount",
            "total_amount",
            "created_at",
        ]
        read_only_fields = fields


class InvoiceDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_code",
            "order_id",
            "customer_id",
            "status",
            "invoice_date",
            "due_date",
            "notes",
            "subtotal",
            "tax_amount",
            "total_amount",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_items(self, obj):
        items = InvoiceService.get_invoice_items(obj.id)
        return InvoiceItemSerializer(items, many=True).data


class InvoiceUpdateSerializer(serializers.Serializer):
    notes = serializers.CharField(required=True, allow_blank=True)
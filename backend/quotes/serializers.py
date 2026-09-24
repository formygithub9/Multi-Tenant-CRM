from decimal import Decimal

from rest_framework import serializers

from quotes.models import Quote, QuoteItem
from quotes.services import QuoteService


class QuoteItemInputSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()

    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    quantity = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    unit_price = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    tax_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
    )


class QuoteCreateSerializer(serializers.ModelSerializer):

    tenant_id = serializers.IntegerField(
        write_only=True,
    )

    items = QuoteItemInputSerializer(
        many=True,
        write_only=True,
    )

    class Meta:
        model = Quote

        fields = (
            "tenant_id",
            "customer_id",
            "deal_id",
            "title",
            "notes",
            "valid_until",
            "items",
        )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one quote item is required."
            )

        return value

    def create(self, validated_data):
        items = validated_data.pop("items")

        return QuoteService.create_quote(
            validated_data=validated_data,
            items=items,
        )


class QuoteItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuoteItem

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


class QuoteListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quote

        fields = (
            "id",
            "quote_code",
            "customer_id",
            "deal_id",
            "title",
            "notes",
            "status",
            "valid_until",
            "subtotal",
            "tax_amount",
            "total_amount",
            "is_active",
            "created_at",
        )


class QuoteDetailSerializer(serializers.ModelSerializer):

    items = serializers.SerializerMethodField()

    class Meta:
        model = Quote

        fields = (
            "id",
            "quote_code",
            "customer_id",
            "deal_id",
            "title",
            "notes",
            "status",
            "valid_until",
            "subtotal",
            "tax_amount",
            "total_amount",
            "is_active",
            "created_at",
            "items",
        )

    def get_items(self, obj):
        items = QuoteService.get_quote_items(obj.id)
        return QuoteItemSerializer(items,many=True,).data
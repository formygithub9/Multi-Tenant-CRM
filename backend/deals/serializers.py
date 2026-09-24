from decimal import Decimal

from rest_framework import serializers

from deals.models import Deal
from deals.services import DealService


class DealValidationMixin:

    def validate(self, attrs):
        amount = attrs.get(
            "amount",
            self.instance.amount if self.instance else Decimal("0"),
        )

        probability = attrs.get(
            "probability",
            self.instance.probability
            if self.instance
            else Decimal("0"),
        )

        if amount < 0:
            raise serializers.ValidationError(
                {"amount": "Amount cannot be negative."}
            )

        if probability < 0 or probability > 100:
            raise serializers.ValidationError(
                {"probability": "Probability must be between 0 and 100."}
            )

        return attrs


class DealCreateSerializer(DealValidationMixin,serializers.ModelSerializer,):
    tenant_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Deal

        fields = (
            "tenant_id",
            "customer_id",
            "title",
            "description",
            "stage",
            "amount",
            "expected_close_date",
            "probability",
        )

    def create(self, validated_data):
        return DealService.create_deal(validated_data)


class DealListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deal

        fields = (
            "id",
            "deal_code",
            "customer_id",
            "title",
            "description",
            "stage",
            "status",
            "amount",
            "expected_close_date",
            "probability",
            "is_active",
            "created_at",
        )


class DealUpdateSerializer(DealValidationMixin,serializers.ModelSerializer,):

    class Meta:
        model = Deal

        fields = (
            "customer_id",
            "title",
            "description",
            "stage",
            "status",
            "amount",
            "expected_close_date",
            "probability",
        )
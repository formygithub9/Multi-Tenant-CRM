
from rest_framework import serializers

from payments.models import Payment


class PaymentCreateSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)
    payment_method = serializers.ChoiceField(choices=Payment.PaymentMethod.choices)
    reference = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class PaymentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            Payment.PaymentStatus.COMPLETED,
            Payment.PaymentStatus.FAILED,
            Payment.PaymentStatus.REFUNDED,
        ]
    )


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "payment_code", "invoice_id", "amount",
            "payment_method", "status", "payment_date", "reference",
            "created_at",
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "tenant_id", "payment_code", "invoice_id", "amount",
            "payment_method", "status", "payment_date", "reference",
            "notes", "created_at", "updated_at",
        ]

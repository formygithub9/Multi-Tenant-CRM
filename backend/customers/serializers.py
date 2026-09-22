from rest_framework import serializers

from customers.models import Customer
from customers.services import CustomerService


class CustomerValidationMixin:

    def validate(self, attrs):

        customer_type = attrs.get(
            "customer_type",
            getattr(
                self.instance,
                "customer_type",
                None,
            ),
        )

        gst_number = attrs.get(
            "gst_number",
            getattr(
                self.instance,
                "gst_number",
                "",
            ),
        )

        if (
            customer_type == Customer.CustomerType.INDIVIDUAL
            and gst_number
        ):
            raise serializers.ValidationError(
                {
                    "gst_number": (
                        "GST is not allowed for Individual customers."
                    )
                }
            )

        if (
            customer_type == Customer.CustomerType.BUSINESS
            and not gst_number
        ):
            raise serializers.ValidationError(
                {
                    "gst_number": (
                        "GST is required for Business customers."
                    )
                }
            )

        return attrs


class CustomerCreateSerializer(serializers.ModelSerializer):
    tenant_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Customer
        fields = (
            "tenant_id",
            "customer_type",
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "gst_number",
            "pan_number",
            "remarks",
        )

    def create(self, validated_data):
        return CustomerService.create_customer(validated_data)


class CustomerListSerializer(serializers.ModelSerializer):

    class Meta:

        model = Customer

        fields = (
            "id",
            "customer_code",
            "customer_type",
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "gst_number",
            "pan_number",
            "remarks",
            "is_active",
            "created_at",
        )


class CustomerUpdateSerializer(CustomerValidationMixin,serializers.ModelSerializer,):

    class Meta:

        model = Customer

        fields = (
            "customer_type",
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "gst_number",
            "pan_number",
            "remarks",
        )
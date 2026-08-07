from rest_framework import serializers

from customers.models import Customer
from customers.services import CustomerService


class CustomerCreateSerializer(serializers.ModelSerializer):

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
        return CustomerService.create_customer(validated_data,)

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
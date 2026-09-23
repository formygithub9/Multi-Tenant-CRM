from rest_framework import serializers

from vendors.models import Vendor
from vendors.services import VendorService


class VendorValidationMixin:

    def validate(self, attrs):
        vendor_type = attrs.get(
            "vendor_type",
            self.instance.vendor_type
            if self.instance
            else Vendor.VendorType.BUSINESS,
        )

        gst_number = attrs.get(
            "gst_number",
            self.instance.gst_number
            if self.instance
            else "",
        )

        if (
            vendor_type == Vendor.VendorType.INDIVIDUAL
            and gst_number
        ):
            raise serializers.ValidationError(
                {
                    "gst_number": (
                        "GST is not allowed for Individual vendors."
                    )
                }
            )

        if (
            vendor_type == Vendor.VendorType.BUSINESS
            and not gst_number
        ):
            raise serializers.ValidationError(
                {
                    "gst_number": (
                        "GST is required for Business vendors."
                    )
                }
            )

        return attrs


class VendorCreateSerializer(
    VendorValidationMixin,
    serializers.ModelSerializer,
):
    tenant_id = serializers.IntegerField(
        write_only=True
    )

    class Meta:
        model = Vendor

        fields = (
            "tenant_id",
            "vendor_type",
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "gst_number",
            "pan_number",
            "address",
            "city",
            "state",
            "pincode",
            "remarks",
        )

    def create(self, validated_data):
        return VendorService.create_vendor(
            validated_data
        )


class VendorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor

        fields = (
            "id",
            "vendor_code",
            "vendor_type",
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "gst_number",
            "pan_number",
            "address",
            "city",
            "state",
            "pincode",
            "remarks",
            "is_active",
            "created_at",
        )


class VendorUpdateSerializer(
    VendorValidationMixin,
    serializers.ModelSerializer,
):

    class Meta:
        model = Vendor

        fields = (
            "vendor_type",
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "gst_number",
            "pan_number",
            "address",
            "city",
            "state",
            "pincode",
            "remarks",
        )
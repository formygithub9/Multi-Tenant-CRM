from rest_framework import serializers
from leads.services import LeadService
from leads.models import Lead


class LeadCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead

        fields = (
            "tenant_id",
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "source",
            "status",
            "notes",
        )

    def validate(self, attrs):

        if not attrs.get("email") and not attrs.get("mobile"):
            raise serializers.ValidationError(
                "Either email or mobile is required."
            )

        return attrs

    def create(self, validated_data):
        return LeadService.create_lead(
            validated_data,
        )
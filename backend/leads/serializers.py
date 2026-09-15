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

class LeadListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead

        fields = (
            "id",
            "lead_code",
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "source",
            "status",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        )

class LeadUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead

        fields = (
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "source",
            "status",
            "notes",
        )

    def validate(self, attrs):

        email = attrs.get(
            "email",
            self.instance.email,
        )

        mobile = attrs.get(
            "mobile",
            self.instance.mobile,
        )

        if not email and not mobile:
            raise serializers.ValidationError(
                "Either email or mobile is required."
            )

        return attrs

class LeadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            "id",
            "lead_code",
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "source",
            "status",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        )

class LeadUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            "contact_name",
            "company_name",
            "email",
            "mobile",
            "source",
            "status",
            "notes",
        )

    def validate(self, attrs):
        lead = self.instance

        new_status = attrs.get(
            "status",
            lead.status,
        )

        # Converted leads should not be modified
        if lead.status == Lead.LeadStatus.CONVERTED:
            raise serializers.ValidationError(
                "Converted leads cannot be updated."
            )

        # A lead should not be manually changed back
        # from CONVERTED because that state is controlled
        # by the conversion workflow.
        if (
            new_status == Lead.LeadStatus.CONVERTED
            and lead.status != Lead.LeadStatus.CONVERTED
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "Use the lead conversion endpoint "
                        "to convert a qualified lead."
                    )
                }
            )

        return attrs
from rest_framework import serializers
from contacts.models import Contact


class ContactCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact

        fields = (
            "tenant_id",
            "customer_id",
            "first_name",
            "last_name",
            "designation",
            "email",
            "mobile",
            "is_primary",
        )

    def validate(self, attrs):

        if not attrs.get("email") and not attrs.get("mobile"):
            raise serializers.ValidationError(
                "Either email or mobile is required."
            )

        return attrs

class ContactListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact

        fields = (
            "id",
            "customer_id",
            "first_name",
            "last_name",
            "designation",
            "email",
            "mobile",
            "is_primary",
            "is_active",
            "created_at",
        )

class ContactUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact

        fields = (
            "first_name",
            "last_name",
            "designation",
            "email",
            "mobile",
            "is_primary",
        )

    def validate(self, attrs):

        email = attrs.get("email",self.instance.email,)
        mobile = attrs.get("mobile",self.instance.mobile,)

        if not email and not mobile:
            raise serializers.ValidationError(
                "Either email or mobile is required."
            )

        return attrs
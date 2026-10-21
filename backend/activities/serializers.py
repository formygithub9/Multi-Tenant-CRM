
from rest_framework import serializers

from activities.models import Activity


class ActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "title", "description", "activity_type", "priority",
            "related_type", "related_id", "assigned_to_id", "due_at",
        ]

    def validate(self, attrs):
        related_type = attrs.get("related_type")
        related_id = attrs.get("related_id")

        if bool(related_type) != bool(related_id):
            raise serializers.ValidationError(
                "related_type and related_id must be supplied together."
            )
        return attrs


class ActivityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "title", "description", "activity_type", "priority",
            "related_type", "related_id", "assigned_to_id", "due_at",
        ]

    def validate(self, attrs):
        related_type = attrs.get("related_type")
        related_id = attrs.get("related_id")

        if ("related_type" in attrs) != ("related_id" in attrs):
            raise serializers.ValidationError(
                "related_type and related_id must be updated together."
            )
        if related_type is not None and related_id is None:
            raise serializers.ValidationError(
                "related_id is required when related_type is supplied."
            )
        return attrs


class ActivityStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Activity.Status.choices)


class ActivityReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "id", "tenant_id", "title", "description",
            "activity_type", "priority", "status",
            "related_type", "related_id", "assigned_to_id",
            "created_by_id", "due_at", "completed_at",
            "created_at", "updated_at",
        ]

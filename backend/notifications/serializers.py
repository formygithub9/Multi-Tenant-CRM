from rest_framework import serializers

from notifications.models import Notification


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "recipient_id", "notification_type", "title", "message",
            "related_type", "related_id",
        ]


class NotificationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "notification_type", "title", "message",
            "related_type", "related_id", "read_at", "created_at",
        ]
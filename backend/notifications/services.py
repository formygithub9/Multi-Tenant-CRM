from django.db import transaction
from django.utils import timezone

from core.db_context import get_current_database
from core.exceptions import NotFoundException
from notifications.models import Notification


class NotificationService:
    @staticmethod
    def get_queryset(tenant_id, user_id, unread_only=False):
        database = get_current_database()
        queryset = Notification.objects.using(database).filter(
            tenant_id=tenant_id,
            recipient_id=user_id,
            is_active=True,
        )
        if unread_only:
            queryset = queryset.filter(read_at__isnull=True)
        return queryset

    @staticmethod
    @transaction.atomic
    def create(tenant_id, recipient_id, title, message, notification_type="SYSTEM", related_type="", related_id=None):
        database = get_current_database()
        with transaction.atomic(using=database):
            return Notification.objects.using(database).create(
                tenant_id=tenant_id,
                recipient_id=recipient_id,
                title=title,
                message=message,
                notification_type=notification_type,
                related_type=related_type,
                related_id=related_id,
            )

    @staticmethod
    @transaction.atomic
    def mark_read(tenant_id, user_id, notification_id):
        database = get_current_database()
        with transaction.atomic(using=database):
            notification = Notification.objects.using(database).filter(
                id=notification_id,
                tenant_id=tenant_id,
                recipient_id=user_id,
                is_active=True,
            ).first()

            if not notification:
                raise NotFoundException("Notification not found.")

            if notification.read_at is None:
                notification.read_at = timezone.now()
                notification.save(using=database, update_fields=["read_at"])

            return notification

    @staticmethod
    @transaction.atomic
    def mark_all_read(tenant_id, user_id):
        database = get_current_database()
        with transaction.atomic(using=database):
            return Notification.objects.using(database).filter(
                tenant_id=tenant_id,
                recipient_id=user_id,
                is_active=True,
                read_at__isnull=True,
            ).update(read_at=timezone.now())

    @staticmethod
    @transaction.atomic
    def delete(tenant_id, user_id, notification_id):
        database = get_current_database()
        with transaction.atomic(using=database):
            notification = Notification.objects.using(database).filter(
                id=notification_id,
                tenant_id=tenant_id,
                recipient_id=user_id,
                is_active=True,
            ).first()

            if not notification:
                raise NotFoundException("Notification not found.")

            notification.is_active = False
            notification.save(using=database, update_fields=["is_active"])
            return notification
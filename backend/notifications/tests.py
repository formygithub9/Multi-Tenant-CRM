
from django.test import TestCase
from django.utils import timezone

from notifications.models import Notification


class NotificationModelTests(TestCase):
    databases = {"default", "shared_db"}

    def setUp(self):
        self.database = "shared_db"
        self.notification = Notification.objects.using(self.database).create(
            tenant_id=1,
            recipient_id=10,
            notification_type="GENERAL",
            title="Test notification",
            message="This is a test notification.",
        )

    def test_notification_is_created(self):
        notification = Notification.objects.using(self.database).get(
            pk=self.notification.pk
        )
        self.assertEqual(notification.title, "Test notification")
        self.assertEqual(notification.recipient_id, 10)
        self.assertTrue(notification.is_active)

    def test_notification_starts_unread(self):
        self.assertIsNone(self.notification.read_at)

    def test_notification_can_be_marked_read(self):
        Notification.objects.using(self.database).filter(
            pk=self.notification.pk
        ).update(read_at=timezone.now())

        self.notification.refresh_from_db(using=self.database)
        self.assertIsNotNone(self.notification.read_at)

    def test_notification_can_be_soft_deleted(self):
        Notification.objects.using(self.database).filter(
            pk=self.notification.pk
        ).update(is_active=False)

        self.notification.refresh_from_db(using=self.database)
        self.assertFalse(self.notification.is_active)

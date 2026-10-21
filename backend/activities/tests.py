
from django.test import TestCase

from activities.models import Activity


class ActivityModelTests(TestCase):
    # databases = {"shared_db"}
    databases = {"default", "shared_db"}

    def setUp(self):
        self.database = "shared_db"
        self.activity = Activity.objects.using(self.database).create(
            tenant_id=1,
            title="Follow up with customer",
            description="Discuss the proposal.",
            activity_type="TASK",
            priority="MEDIUM",
            status="OPEN",
            related_type="CUSTOMER",
            related_id=100,
            assigned_to_id=10,
            created_by_id=10,
        )

    def test_activity_is_created(self):
        activity = Activity.objects.using(self.database).get(
            pk=self.activity.pk
        )
        self.assertEqual(activity.title, "Follow up with customer")
        self.assertEqual(activity.tenant_id, 1)
        self.assertTrue(activity.is_active)

    def test_activity_starts_open(self):
        self.assertEqual(self.activity.status, "OPEN")

    def test_activity_can_be_completed(self):
        Activity.objects.using(self.database).filter(
            pk=self.activity.pk
        ).update(status="COMPLETED")

        self.activity.refresh_from_db(using=self.database)
        self.assertEqual(self.activity.status, "COMPLETED")

    def test_activity_can_be_soft_deleted(self):
        Activity.objects.using(self.database).filter(
            pk=self.activity.pk
        ).update(is_active=False)

        self.activity.refresh_from_db(using=self.database)
        self.assertFalse(self.activity.is_active)

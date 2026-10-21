
from django.db import transaction
from django.utils import timezone

from core.db_context import get_current_database
from core.exceptions import BadRequestException, NotFoundException
from activities.models import Activity


class ActivityService:
    @staticmethod
    def get_queryset(tenant_id, filters=None):
        database = get_current_database()
        filters = filters or {}

        queryset = Activity.objects.using(database).filter(
            tenant_id=tenant_id,
            is_active=True,
        )

        if filters.get("status"):
            queryset = queryset.filter(status=filters["status"])
        if filters.get("priority"):
            queryset = queryset.filter(priority=filters["priority"])
        if filters.get("activity_type"):
            queryset = queryset.filter(activity_type=filters["activity_type"])
        if filters.get("assigned_to_id"):
            queryset = queryset.filter(assigned_to_id=filters["assigned_to_id"])
        if filters.get("related_type"):
            queryset = queryset.filter(related_type=filters["related_type"])
        if filters.get("related_id"):
            queryset = queryset.filter(related_id=filters["related_id"])

        return queryset

    @staticmethod
    def get_by_id(tenant_id, activity_id, lock=False):
        database = get_current_database()
        queryset = Activity.objects.using(database).filter(
            tenant_id=tenant_id,
            id=activity_id,
            is_active=True,
        )
        if lock:
            queryset = queryset.select_for_update()

        activity = queryset.first()
        if not activity:
            raise NotFoundException("Activity not found.")
        return activity

    @staticmethod
    @transaction.atomic
    def create(tenant_id, user_id, validated_data):
        database = get_current_database()
        data = dict(validated_data)

        if data.get("status") == Activity.Status.COMPLETED:
            data["completed_at"] = timezone.now()

        return Activity.objects.using(database).create(
            tenant_id=tenant_id,
            created_by_id=user_id,
            **data,
        )

    @staticmethod
    @transaction.atomic
    def update(tenant_id, activity_id, validated_data):
        database = get_current_database()
        activity = ActivityService.get_by_id(tenant_id, activity_id, lock=True)

        if activity.status in (Activity.Status.COMPLETED, Activity.Status.CANCELLED):
            raise BadRequestException("Completed or cancelled activities cannot be edited.")

        for field, value in validated_data.items():
            setattr(activity, field, value)

        if activity.status == Activity.Status.COMPLETED:
            activity.completed_at = timezone.now()
        else:
            activity.completed_at = None

        activity.save(using=database)
        return activity

    @staticmethod
    @transaction.atomic
    def change_status(tenant_id, activity_id, new_status):
        database = get_current_database()
        activity = ActivityService.get_by_id(tenant_id, activity_id, lock=True)

        allowed = {
            Activity.Status.OPEN: {Activity.Status.IN_PROGRESS, Activity.Status.COMPLETED, Activity.Status.CANCELLED},
            Activity.Status.IN_PROGRESS: {Activity.Status.OPEN, Activity.Status.COMPLETED, Activity.Status.CANCELLED},
            Activity.Status.COMPLETED: set(),
            Activity.Status.CANCELLED: set(),
        }

        if new_status not in allowed[activity.status]:
            raise BadRequestException(
                f"Cannot change status from {activity.status} to {new_status}."
            )

        activity.status = new_status
        activity.completed_at = timezone.now() if new_status == Activity.Status.COMPLETED else None
        activity.save(using=database, update_fields=["status", "completed_at", "updated_at"])
        return activity

    @staticmethod
    @transaction.atomic
    def delete(tenant_id, activity_id):
        database = get_current_database()
        activity = ActivityService.get_by_id(tenant_id, activity_id, lock=True)
        activity.is_active = False
        activity.save(using=database, update_fields=["is_active", "updated_at"])
        return activity

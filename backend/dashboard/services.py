from django.apps import apps
from django.db.models import Count

from core.db_context import get_current_database


class DashboardService:
    MODELS = {
        "customers": ("customers", "Customer"),
        "contacts": ("contacts", "Contact"),
        "leads": ("leads", "Lead"),
        "deals": ("deals", "Deal"),
        "quotes": ("quotes", "Quote"),
        "orders": ("orders", "Order"),
        "invoices": ("invoices", "Invoice"),
        "payments": ("payments", "Payment"),
        "activities": ("activities", "Activity"),
    }

    @staticmethod
    def _get_model(app_label, model_name):
        return apps.get_model(app_label, model_name)

    @classmethod
    def _count_model(cls, model, tenant_id, database):
        queryset = model.objects.using(database).filter(tenant_id=tenant_id)

        field_names = {field.name for field in model._meta.get_fields()}

        if "is_active" in field_names:
            queryset = queryset.filter(is_active=True)

        result = {"total": queryset.count()}

        if "status" in field_names:
            result["by_status"] = {
                row["status"]: row["count"]
                for row in queryset.values("status").annotate(
                    count=Count("id")
                ).order_by("status")
            }

        return result

    @classmethod
    def get_summary(cls, tenant_id):
        database = get_current_database()
        summary = {}

        for key, (app_label, model_name) in cls.MODELS.items():
            model = cls._get_model(app_label, model_name)
            summary[key] = cls._count_model(model, tenant_id, database)

        return summary
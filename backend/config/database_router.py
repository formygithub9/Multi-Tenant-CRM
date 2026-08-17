from core.db_context import get_current_database

class DatabaseRouter:

    DEFAULT_APPS = {
        "tenants",
    }

    TENANT_APPS = {
        "accounts",
        "authorization",
        "rbac",
        "customers",
        "common",
        "contacts",
        "leads",

        "auth",
        "contenttypes",
        "admin",
        "sessions",
    }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.DEFAULT_APPS:
            return "default"

        if model._meta.app_label in self.TENANT_APPS:
            return get_current_database()

        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.DEFAULT_APPS:
            return "default"

        if model._meta.app_label in self.TENANT_APPS:
            return get_current_database()

        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label in self.DEFAULT_APPS:
            return db == "default"

        if app_label in self.TENANT_APPS:
            # return db == "shared_db"
            return db in ("shared_db", "enterprise_db")

        return None
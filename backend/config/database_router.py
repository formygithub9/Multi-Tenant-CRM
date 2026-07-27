class DatabaseRouter:

    DEFAULT_APPS = {
        "accounts",
        "tenants",
        "authorization",
        "auth",
        "contenttypes",
        "admin",
        "sessions",
    }

    TENANT_APPS = {
        "customers",
    }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.DEFAULT_APPS:
            return "default"

        if model._meta.app_label in self.TENANT_APPS:
            return "tenant_db"

        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.DEFAULT_APPS:
            return "default"

        if model._meta.app_label in self.TENANT_APPS:
            return "tenant_db"

        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label in self.DEFAULT_APPS:
            return db == "default"

        if app_label in self.TENANT_APPS:
            return db == "tenant_db"

        return None
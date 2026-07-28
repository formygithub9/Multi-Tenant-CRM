from threading import local

_thread_locals = local()


def set_current_database(database_alias):
    _thread_locals.database_alias = database_alias


def get_current_database():
    return getattr(_thread_locals, "database_alias", "shared_db")


def clear_current_database():
    if hasattr(_thread_locals, "database_alias"):
        del _thread_locals.database_alias
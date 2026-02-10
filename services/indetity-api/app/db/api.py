# repo/repository.py
from .executor import PostgresExecutor
from .protocols import QueryExecutor


_db: QueryExecutor | None = None


def get_db() -> QueryExecutor:
    global _db
    if _db is None:
        _db = PostgresExecutor()
    return _db
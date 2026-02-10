import psycopg
from psycopg_pool import ConnectionPool
from .config import PostgresConfig

_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    global _pool

    if _pool is None:
        cfg = PostgresConfig.from_env()
        _pool = ConnectionPool(
            conninfo=cfg.dsn,
            min_size=1,
            max_size=10,
            open=True,
        )

    return _pool
# repo/executor.py
from .connection import get_pool

class PostgresExecutor:
    def query(self, query: str, params: tuple | None = None) -> list[tuple]:
        with get_pool().connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def execute(self, query: str, params: tuple | None = None) -> int:
        with get_pool().connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.rowcount
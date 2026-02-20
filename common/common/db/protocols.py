# repo/protocols.py
from typing import Protocol


class QueryExecutor(Protocol):
    # This is for queries, which return a list of tuples (rows) (e.g. selects or inserts with RETURNING)
    def query(self, query: str, params: tuple | None = None) -> list[tuple]: ...
    # This is for insert/update/delete queries, which return the number of affected rows
    def execute(self, query: str, params: tuple | None = None) -> int: ...
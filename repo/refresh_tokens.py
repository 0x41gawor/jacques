# repo/refresh_tokens.py
from datetime import datetime
from typing import Optional
from uuid import UUID

from db.protocols import QueryExecutor


class RefreshTokenRepository:
    def __init__(self, db: QueryExecutor):
        self._db = db

    def insert(
        self,
        *,
        user_id: str,
        token_hash: str,
        expires_at: datetime,
    ) -> None:
        self._db.execute(
            """
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES (%s, %s, %s)
            """,
            (user_id, token_hash, expires_at),
        )

    def revoke(self, *, token_hash: str) -> None:
        self._db.execute(
            """
            UPDATE refresh_tokens
            SET revoked_at = now()
            WHERE token_hash = %s
            """,
            (token_hash,),
        )

    def find_valid(self, *, token_hash: str) -> Optional[tuple]:
        rows = self._db.query(
            """
            SELECT id, user_id, expires_at
            FROM refresh_tokens
            WHERE token_hash = %s
              AND revoked_at IS NULL
              AND expires_at > now()
            """,
            (token_hash,),
        )
        return rows[0] if rows else None

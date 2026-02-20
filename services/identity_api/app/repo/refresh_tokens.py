# repo/refresh_tokens.py
from datetime import datetime
from typing import Optional
from uuid import UUID

from common.db.protocols import QueryExecutor
from common.logging.trace import trace
from .models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: QueryExecutor):
        self._db = db
    @trace
    def insert(
        self,
        *,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> UUID:
        rows = self._db.query(
            """
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (user_id, token_hash, expires_at),
        )

        return rows[0][0]


    def revoke(self, *, token_hash: str) -> None:
        self._db.execute(
            """
            UPDATE refresh_tokens
            SET revoked_at = now()
            WHERE token_hash = %s
            """,
            (token_hash,),
        )

    def find_valid(self, *, token_hash: str) -> RefreshToken | None:
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

        if not rows:
            return None

        row = rows[0]

        return RefreshToken(
            id=row[0],
            user_id=row[1],
            expires_at=row[2],
        )


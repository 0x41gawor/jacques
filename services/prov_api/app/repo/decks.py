from uuid import UUID
from typing import Optional

from common.db.protocols import QueryExecutor
from .models import Deck


class DeckRepository:
    def __init__(self, db: QueryExecutor):
        self._db = db

    def find_default_by_user_id(self, user_id: UUID) -> Optional[Deck]:
        rows = self._db.query(
            """
            SELECT id, owner_id, name, is_default, created_at
            FROM decks
            WHERE owner_id = %s
              AND is_default = true
            """,
            (user_id,),
        )

        if not rows:
            return None

        row = rows[0]

        return Deck(
            id=row[0],
            owner_id=row[1],
            name=row[2],
            is_default=row[3],
            created_at=row[4],
        )

    def find_by_user_id(self, user_id: UUID) -> list[Deck]:
        rows = self._db.query(
            """
            SELECT id, owner_id, name, is_default, created_at
            FROM decks
            WHERE owner_id = %s
            ORDER BY created_at
            """,
            (user_id,),
        )

        return [
            Deck(
                id=row[0],
                owner_id=row[1],
                name=row[2],
                is_default=row[3],
                created_at=row[4],
            )
            for row in rows
        ]

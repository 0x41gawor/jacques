from uuid import UUID

from common.db.protocols import QueryExecutor
from .models import Deck


class DeckRepository:
    def __init__(self, db: QueryExecutor):
        self._db = db

    def insert_default(self, *, owner_id: UUID) -> Deck:
        rows = self._db.query(
            """
            INSERT INTO decks (owner_id, is_default)
            VALUES (%s, true)
            RETURNING id, owner_id, name, is_default, created_at
            """,
            (owner_id,),
        )

        row = rows[0]

        return Deck(
            id=row[0],
            owner_id=row[1],
            name=row[2],
            is_default=row[3],
            created_at=row[4],
        )

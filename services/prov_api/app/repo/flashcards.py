import json
from uuid import UUID
from datetime import datetime

from common.db.protocols import QueryExecutor
from common.logging.trace import trace
from app.service.model.flashcard import Flashcard


class FlashcardRepository:
    def __init__(self, db: QueryExecutor):
        self._db = db
        
    @trace
    def insert(
        self,
        *,
        deck_id: UUID,
        flashcard: Flashcard,
    ) -> UUID:
        """
        Inserts flashcard into DB.
        Returns generated flashcard id.
        """

        front_json = flashcard.to_dict()["front"]
        reverse_json = flashcard.to_dict()["reverse"]

        rows = self._db.query(
            """
            INSERT INTO flashcards (deck_id, front_json, reverse_json)
            VALUES (%s, %s::jsonb, %s::jsonb)
            RETURNING id
            """,
            (
                deck_id,
                json.dumps(front_json),
                json.dumps(reverse_json),
            ),
        )

        return rows[0][0]

# repo/users.py
from typing import Optional
from psycopg.errors import UniqueViolation
from .exceptions import UserAlreadyExists

from app.db.protocols import QueryExecutor
from .models import User


class UserRepository:
    def __init__(self, db: QueryExecutor):
        self._db = db

    def find_by_google_id(self, google_id: str) -> Optional[User]:
        rows = self._db.query(
            """
            SELECT id, google_id, name, created_at
            FROM users
            WHERE google_id = %s
            """,
            (google_id,),
        )
        # Jęśli nie znaleziono użytkownika, zwracamy None
        if not rows:
            return None

        # Zakładamy UNIQUE → max 1 wiersz
        row = rows[0]

        return User(
            id=row[0],
            google_id=row[1],
            name=row[2],
            created_at=row[3],
        )

    def create_user(self, google_id: str, name: str | None) -> User:
        try:
            rows = self._db.query(
                """
                INSERT INTO users (google_id, name)
                VALUES (%s, %s)
                RETURNING id, google_id, name, created_at
                """,
                (google_id, name),
            )
        except UniqueViolation:
            raise UserAlreadyExists(google_id)

        # RETURNING zawsze zwraca dokładnie jeden wiersz
        row = rows[0]

        return User(
            id=row[0],
            google_id=row[1],
            name=row[2],
            created_at=row[3],
        )
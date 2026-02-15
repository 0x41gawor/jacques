# repo/models.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class User:
    id: UUID
    google_id: str
    name: str | None
    created_at: datetime

@dataclass(frozen=True)
class RefreshToken:
    id: UUID
    user_id: UUID
    expires_at: datetime

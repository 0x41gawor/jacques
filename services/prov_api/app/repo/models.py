from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Deck:
    id: UUID
    owner_id: UUID
    name: str
    is_default: bool
    created_at: datetime

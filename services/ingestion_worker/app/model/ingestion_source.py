from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class IngestionSource:
    id: UUID
    user_id: UUID
    source_type: str
    credential_json: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_synced_at: datetime | None
    next_sync_at: datetime
    last_status: str | None
    last_error: str | None
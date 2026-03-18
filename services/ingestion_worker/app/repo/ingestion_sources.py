from __future__ import annotations

from datetime import datetime
from uuid import UUID

from common.db.protocols import QueryExecutor
from common.logging.trace import trace

from app.model.ingestion_source import IngestionSource


class IngestionSourceRepository:
    def __init__(self, db: QueryExecutor):
        self._db = db

    @trace
    def find_due(self, limit: int = 10) -> list[IngestionSource]:
        rows = self._db.query(
            """
            SELECT
                id,
                user_id,
                source_type,
                credential_json,
                is_active,
                created_at,
                updated_at,
                last_synced_at,
                next_sync_at,
                last_status,
                last_error
            FROM ingestion_sources
            WHERE is_active = true
              AND next_sync_at <= now()
            ORDER BY next_sync_at ASC
            LIMIT %s
            """,
            (limit,),
        )

        return [self._map_row(row) for row in rows]

    @trace
    def mark_success(
        self,
        *,
        source_id: UUID,
        synced_at: datetime,
        next_sync_at: datetime,
    ) -> None:
        self._db.execute(
            """
            UPDATE ingestion_sources
            SET
                last_synced_at = %s,
                next_sync_at = %s,
                last_status = 'ok',
                last_error = NULL,
                updated_at = now()
            WHERE id = %s
            """,
            (synced_at, next_sync_at, source_id),
        )

    @trace
    def mark_failure(
        self,
        *,
        source_id: UUID,
        error: str,
        next_sync_at: datetime,
    ) -> None:
        self._db.execute(
            """
            UPDATE ingestion_sources
            SET
                last_status = 'fail',
                last_error = %s,
                next_sync_at = %s,
                updated_at = now()
            WHERE id = %s
            """,
            (error[:1000], next_sync_at, source_id),
        )

    @staticmethod
    def _map_row(row: tuple) -> IngestionSource:
        return IngestionSource(
            id=row[0],
            user_id=row[1],
            source_type=row[2],
            credential_json=row[3],
            is_active=row[4],
            created_at=row[5],
            updated_at=row[6],
            last_synced_at=row[7],
            next_sync_at=row[8],
            last_status=row[9],
            last_error=row[10],
        )
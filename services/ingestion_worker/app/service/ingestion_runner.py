from __future__ import annotations

from datetime import datetime, timedelta, timezone

from common.logging.mixin import LoggingMixin
from common.logging.trace import trace

from app.repo.ingestion_sources import IngestionSourceRepository


class IngestionRunner(LoggingMixin):
    def __init__(
        self,
        *,
        source_repo: IngestionSourceRepository,
        readwise_service,
        identity_api_client,
        prov_api_client,
    ):
        self._source_repo = source_repo
        self._readwise_service = readwise_service
        self._identity_api_client = identity_api_client
        self._prov_api_client = prov_api_client

    @trace
    def run_once(self, batch_size: int = 10) -> None:
        due_sources = self._source_repo.find_due(limit=batch_size)

        self.logger.info(
            "Fetched due ingestion sources",
            extra={
                "batch_size": batch_size,
                "due_sources_count": len(due_sources),
            },
        )

        for source in due_sources:
            self.logger.info(
                "Processing ingestion source",
                extra={
                    "source_id": str(source.id),
                    "user_id": str(source.user_id),
                    "source_type": source.source_type,
                    "last_synced_at": (
                        source.last_synced_at.isoformat()
                        if source.last_synced_at else None
                    ),
                    "next_sync_at": source.next_sync_at.isoformat(),
                },
            )

            try:
                if source.source_type != "readwise":
                    raise RuntimeError(
                        f"unsupported source_type={source.source_type}"
                    )

                token = source.credential_json["token"]

                date_from = (
                    source.last_synced_at
                    or datetime(2026, 3, 17, tzinfo=timezone.utc)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")

                date_to = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

                words = self._readwise_service.fetch_words(
                    token=token,
                    date_from=date_from,
                    date_to=date_to,
                )

                self.logger.info(
                    "Fetched words for source",
                    extra={
                        "source_id": str(source.id),
                        "user_id": str(source.user_id),
                        "words_count": len(words),
                    },
                )

                user_jwt = self._identity_api_client.issue_user_token(
                    user_id=str(source.user_id)
                )

                for word in words:
                    self._prov_api_client.generate_flashcard(
                        token=user_jwt,
                        word=word,
                    )

                now = datetime.now(timezone.utc)
                next_sync_at = now + timedelta(hours=24)

                self._source_repo.mark_success(
                    source_id=source.id,
                    synced_at=now,
                    next_sync_at=next_sync_at,
                )

                self.logger.info(
                    "Ingestion source processed successfully",
                    extra={
                        "source_id": str(source.id),
                        "user_id": str(source.user_id),
                        "words_count": len(words),
                        "next_sync_at": next_sync_at.isoformat(),
                    },
                )

            except Exception as e:
                next_retry_at = datetime.now(timezone.utc) + timedelta(hours=1)

                self._source_repo.mark_failure(
                    source_id=source.id,
                    error=str(e),
                    next_sync_at=next_retry_at,
                )

                self.logger.exception(
                    "Failed to process ingestion source",
                    extra={
                        "source_id": str(source.id),
                        "user_id": str(source.user_id),
                        "next_retry_at": next_retry_at.isoformat(),
                    },
                )
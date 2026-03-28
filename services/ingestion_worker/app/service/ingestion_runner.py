from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone

from common.logging.mixin import LoggingMixin
from common.logging.trace import trace

from app.repo.ingestion_sources import IngestionSourceRepository
from app.service.prov_api_client import (
    ProvApiPermanentError,
    ProvApiTransientError,
    ProvApiUnauthorizedError,
)


class IngestionRunner(LoggingMixin):
    def __init__(
        self,
        *,
        source_repo: IngestionSourceRepository,
        readwise_service,
        identity_api_client,
        prov_api_client,
        max_attempts_per_word: int = 3,
    ):
        self._source_repo = source_repo
        self._readwise_service = readwise_service
        self._identity_api_client = identity_api_client
        self._prov_api_client = prov_api_client
        self._max_attempts_per_word = max_attempts_per_word

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
                        if source.last_synced_at
                        else None
                    ),
                    "next_sync_at": source.next_sync_at.isoformat(),
                },
            )

            try:
                self._process_source(source)
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

    def _process_source(self, source) -> None:
        if source.source_type != "readwise":
            raise RuntimeError(f"unsupported source_type={source.source_type}")

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

        if not words:
            now = datetime.now(timezone.utc)
            next_sync_at = now + timedelta(hours=24)

            self._source_repo.mark_success(
                source_id=source.id,
                synced_at=now,
                next_sync_at=next_sync_at,
            )

            self.logger.info(
                "No words to process for source",
                extra={
                    "source_id": str(source.id),
                    "user_id": str(source.user_id),
                    "next_sync_at": next_sync_at.isoformat(),
                },
            )
            return

        user_jwt = self._identity_api_client.issue_user_token(
            user_id=str(source.user_id)
        )

        queue = deque(words)
        attempts: dict[str, int] = {}
        failed_words: list[str] = []
        success_count = 0

        max_total_attempts = max(len(words) * self._max_attempts_per_word * 2, 10)
        total_attempts = 0

        while queue:
            if total_attempts >= max_total_attempts:
                remaining_words = list(queue)
                failed_words.extend(remaining_words)

                self.logger.error(
                    "Aborting word processing due to max total attempts safeguard",
                    extra={
                        "source_id": str(source.id),
                        "user_id": str(source.user_id),
                        "max_total_attempts": max_total_attempts,
                        "remaining_words_count": len(remaining_words),
                        "remaining_words_preview": remaining_words[:20],
                    },
                )
                break

            word = queue.popleft()
            total_attempts += 1
            attempts.setdefault(word, 0)

            try:
                self._prov_api_client.generate_flashcard(
                    token=user_jwt,
                    word=word,
                )
                success_count += 1

            except ProvApiUnauthorizedError as e:
                attempts[word] += 1

                self.logger.warning(
                    "User token expired or unauthorized, refreshing token",
                    extra={
                        "source_id": str(source.id),
                        "user_id": str(source.user_id),
                        "word": word,
                        "attempt": attempts[word],
                        "max_attempts": self._max_attempts_per_word,
                        "error": str(e),
                    },
                )

                if attempts[word] >= self._max_attempts_per_word:
                    failed_words.append(word)
                    continue

                user_jwt = self._identity_api_client.issue_user_token(
                    user_id=str(source.user_id)
                )
                queue.appendleft(word)

            except ProvApiTransientError as e:
                attempts[word] += 1

                self.logger.warning(
                    "Transient prov-api failure, moving word to queue tail",
                    extra={
                        "source_id": str(source.id),
                        "user_id": str(source.user_id),
                        "word": word,
                        "attempt": attempts[word],
                        "max_attempts": self._max_attempts_per_word,
                        "error": str(e),
                    },
                )

                if attempts[word] < self._max_attempts_per_word:
                    queue.append(word)
                else:
                    failed_words.append(word)

            except ProvApiPermanentError as e:
                attempts[word] += 1

                self.logger.error(
                    "Permanent prov-api failure, skipping word",
                    extra={
                        "source_id": str(source.id),
                        "user_id": str(source.user_id),
                        "word": word,
                        "attempt": attempts[word],
                        "error": str(e),
                    },
                )

                failed_words.append(word)

        now = datetime.now(timezone.utc)
        next_sync_at = now + timedelta(hours=24)

        if failed_words:
            error_summary = (
                f"Skipped {len(failed_words)} word(s): "
                + ", ".join(failed_words[:20])
            )

            self._source_repo.mark_partial_success(
                source_id=source.id,
                synced_at=now,
                next_sync_at=next_sync_at,
                error=error_summary,
            )

            self.logger.warning(
                "Ingestion source processed partially",
                extra={
                    "source_id": str(source.id),
                    "user_id": str(source.user_id),
                    "success_count": success_count,
                    "failed_words_count": len(failed_words),
                    "failed_words_preview": failed_words[:20],
                    "next_sync_at": next_sync_at.isoformat(),
                },
            )
        else:
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
                    "success_count": success_count,
                    "next_sync_at": next_sync_at.isoformat(),
                },
            )
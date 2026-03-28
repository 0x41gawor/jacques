from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock


@dataclass
class WorkerRuntimeState:
    last_loop_started_at: datetime | None = None
    last_loop_finished_at: datetime | None = None
    last_loop_status: str | None = None
    last_loop_error: str | None = None
    current_iteration_running: bool = False

    _lock: Lock = field(default_factory=Lock, repr=False)

    def mark_loop_started(self) -> None:
        with self._lock:
            self.last_loop_started_at = datetime.now(timezone.utc)
            self.current_iteration_running = True
            self.last_loop_error = None

    def mark_loop_success(self) -> None:
        with self._lock:
            self.last_loop_finished_at = datetime.now(timezone.utc)
            self.last_loop_status = "ok"
            self.current_iteration_running = False
            self.last_loop_error = None

    def mark_loop_failure(self, error: str) -> None:
        with self._lock:
            self.last_loop_finished_at = datetime.now(timezone.utc)
            self.last_loop_status = "fail"
            self.current_iteration_running = False
            self.last_loop_error = error[:1000]

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "last_loop_started_at": (
                    self.last_loop_started_at.isoformat()
                    if self.last_loop_started_at else None
                ),
                "last_loop_finished_at": (
                    self.last_loop_finished_at.isoformat()
                    if self.last_loop_finished_at else None
                ),
                "last_loop_status": self.last_loop_status,
                "last_loop_error": self.last_loop_error,
                "current_iteration_running": self.current_iteration_running,
            }
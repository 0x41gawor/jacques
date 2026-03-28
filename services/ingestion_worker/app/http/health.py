from __future__ import annotations

from datetime import datetime, timezone, timedelta

from common.health.base import HealthCheck


class WorkerLoopHealthCheck(HealthCheck):
    name = "worker_loop"

    def __init__(self, runtime_state, max_idle_seconds: int):
        self._runtime_state = runtime_state
        self._max_idle_seconds = max_idle_seconds

    def check(self):
        snap = self._runtime_state.snapshot()

        last_finished_raw = snap["last_loop_finished_at"]
        running = snap["current_iteration_running"]

        if running:
            return {
                "status": "ok",
                "details": snap,
            }

        if not last_finished_raw:
            return {
                "status": "ok",
                "details": snap,
            }

        last_finished = datetime.fromisoformat(last_finished_raw)
        now = datetime.now(timezone.utc)

        if now - last_finished > timedelta(seconds=self._max_idle_seconds):
            return {
                "status": "fail",
                "error": "worker_loop_stalled",
                "details": snap,
            }

        return {
            "status": "ok",
            "details": snap,
        }
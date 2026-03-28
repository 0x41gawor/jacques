from __future__ import annotations

import flask

from common.db.executor import PostgresExecutor
from common.logging.http import register_request_logging
from common.health.base import HealthRegistry
from common.health.database import DatabaseHealthCheck
from common.health.flask import create_health_blueprint

from app.http.health import WorkerLoopHealthCheck


def create_app(*, runtime_state, max_idle_seconds: int):
    app = flask.Flask(__name__)

    db = PostgresExecutor()

    api_bp = flask.Blueprint("api", __name__, url_prefix="/api/v1")
    register_request_logging(api_bp)

    health_registry = HealthRegistry()
    health_registry.register(DatabaseHealthCheck(db))
    health_registry.register(
        WorkerLoopHealthCheck(
            runtime_state=runtime_state,
            max_idle_seconds=max_idle_seconds,
        )
    )

    api_bp.register_blueprint(create_health_blueprint(registry=health_registry))
    app.register_blueprint(api_bp)

    return app
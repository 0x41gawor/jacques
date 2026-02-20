"""
Logs for HTTP layer.

Implementation as middleware that takes `app.`

Usage:
from common.http.request_logging import register_request_logging

def create_app():
    app = Flask(__name__)

    register_request_logging(app)

    return app
"""
import logging
import time
import uuid
from flask import request, g


def register_request_logging(app, *, logger_name: str = "http"):
    logger = logging.getLogger(logger_name)

    @app.before_request
    def _log_request():
        g.request_id = str(uuid.uuid4())
        g._start_time = time.perf_counter()

        logger.info(
            "REQUEST",
            extra={
                "request_id": g.request_id,
                "method": request.method,
                "path": request.path,
                "query": request.query_string.decode(),
                "remote_addr": request.remote_addr,
            },
        )

    @app.after_request
    def _log_response(response):
        duration = round(
            (time.perf_counter() - getattr(g, "_start_time", time.perf_counter())) * 1000,
            3,
        )

        logger.info(
            "RESPONSE",
            extra={
                "request_id": getattr(g, "request_id", None),
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration,
            },
        )

        return response
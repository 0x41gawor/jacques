from __future__ import annotations

import os

from flask import Blueprint, jsonify, request

from common.logging.mixin import LoggingMixin
from common.logging.trace import trace

from app.service.auth.jwt import issue_internal_access_token


class InternalBlueprint(LoggingMixin):
    def __init__(self):
        self._bp = Blueprint("internal", __name__, url_prefix="/internal")
        self._register_routes()

    def blueprint(self) -> Blueprint:
        return self._bp

    def _register_routes(self) -> None:
        self._bp.add_url_rule(
            "/token",
            view_func=self.issue_token,
            methods=["POST"],
        )

    @trace
    def issue_token(self):
        auth_header = request.headers.get("Authorization")

        expected_token = os.environ["JACQUES_JWT_SECRET"]

        if not auth_header:
            return jsonify({"error": "missing_authorization_header"}), 401

        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "invalid_authorization_header_format"}), 401

        provided_token = parts[1].strip()
        if provided_token != expected_token:
            return jsonify({"error": "invalid_internal_service_token"}), 401

        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "missing_user_id"}), 400

        self.logger.info(
            "Issuing internal access token",
            extra={
                "user_id": user_id,
            },
        )

        access_token, expires_in = issue_internal_access_token(user_id=user_id)

        return jsonify({
            "access_token": access_token,
            "expires_in": expires_in,
        }), 200
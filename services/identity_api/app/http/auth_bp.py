# app/http/auth_bp.py
from __future__ import annotations

from flask import Blueprint, jsonify, request
from common.logging.mixin import LoggingMixin

from common.logging.trace import trace

from app.service.exceptions import (
    MissingOAuthCode,
    OAuthExchangeFailed,
    InvalidIdToken,
)


class AuthBlueprint(LoggingMixin):
    def __init__(self, *, oauth_callback_service):
        self._oauth_callback_service = oauth_callback_service

        self._bp = Blueprint("auth", __name__, url_prefix="/auth")
        self._register_routes()

    def blueprint(self) -> Blueprint:
        return self._bp

    # -------------------------
    # Route registration
    # -------------------------

    def _register_routes(self) -> None:
        self._bp.add_url_rule(
            "/google/callback",
            view_func=self.google_callback,
            methods=["GET"],
        )

    # -------------------------
    # Handlers
    # -------------------------
    @trace
    def google_callback(self):
        code = request.args.get("code")
        state = request.args.get("state")

        self.logger.info(
            "OAuth callback received",
            extra={
                "has_code": bool(code),
                "has_state": bool(state),
            },
        )

        try:
            tokens = self._oauth_callback_service.handle_callback(
                code=code,
                state=state,
            )

        except MissingOAuthCode as e:
            self.logger.warning(
                "Missing OAuth code or state",
                extra={"error": str(e)},
            )
            return jsonify({"error": f"missing_code_or_state {e}"}), 400

        except OAuthExchangeFailed as e:
            self.logger.error(
                "OAuth exchange failed",
                extra={"error": str(e)},
            )
            return jsonify({"error": f"oauth_exchange_failed {e}"}), 502

        except InvalidIdToken as e:
            self.logger.warning(
                "Invalid ID token",
                extra={"error": str(e)},
            )
            return jsonify({"error": f"invalid_id_token {e}"}), 401

        self.logger.info("OAuth callback successful")

        return jsonify(tokens), 200

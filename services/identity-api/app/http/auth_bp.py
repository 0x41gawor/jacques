# app/http/auth_bp.py
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.service.exceptions import MissingOAuthCode, OAuthExchangeFailed, InvalidIdToken


def create_auth_blueprint(*, oauth_callback_service):
    bp = Blueprint("auth", __name__, url_prefix="/auth")

    @bp.route("/google/callback", methods=["GET"])
    def google_callback():
        code = request.args.get("code")
        state = request.args.get("state")

        try:
            tokens = oauth_callback_service.handle_callback(code=code, state=state)
        except MissingOAuthCode as e:
            return jsonify({"error": f"missing_code_or_state {e}"}), 400
        except OAuthExchangeFailed as e:
            return jsonify({"error": f"oauth_exchange_failed {e}"}), 502
        except InvalidIdToken as e:
            return jsonify({"error": f"invalid_id_token {e}"}), 401

        return jsonify(tokens), 200

    return bp

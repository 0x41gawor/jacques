from __future__ import annotations

from functools import wraps
from flask import request, jsonify, g

from app.service.auth.jwt import (
    parse_bearer_token,
    verify_access_token,
    MissingBearerToken,
    InvalidToken,
)


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            token = parse_bearer_token(request.headers.get("Authorization"))
            ctx = verify_access_token(token)
        except MissingBearerToken as e:
            return jsonify({"error": str(e)}), 401
        except InvalidToken as e:
            return jsonify({"error": str(e)}), 401

        # minimalny "context injection"
        g.user_id = ctx.user_id
        g.jwt_claims = ctx.claims

        return fn(*args, **kwargs)

    return wrapper

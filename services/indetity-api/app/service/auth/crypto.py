# auth/crypto.py
import hashlib
import hmac
import os

from app.service.auth.config import REFRESH_TOKEN_PEPPER


def hash_refresh_token(token: str) -> str:
    """
    HMAC-SHA256 — odporne na rainbow tables
    """
    secret = REFRESH_TOKEN_PEPPER
    return hmac.new(
        secret.encode(),
        token.encode(),
        hashlib.sha256
    ).hexdigest()

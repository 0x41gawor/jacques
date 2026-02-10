# auth/crypto.py
import hashlib
import hmac
import os

def hash_refresh_token(token: str) -> str:
    """
    HMAC-SHA256 — odporne na rainbow tables
    """
    secret = os.environ["JACQUES_REFRESH_TOKEN_PEPPER"]
    return hmac.new(
        secret.encode(),
        token.encode(),
        hashlib.sha256
    ).hexdigest()

# auth/jwt.py
import time
import jwt

from auth.config import (
    JWT_SECRET,
    JWT_ISSUER,
    JWT_ALGORITHM,
    ACCESS_TOKEN_TTL_SECONDS,
)

def issue_access_token(user_id: str) -> str:
    now = int(time.time())

    payload = {
        "sub": user_id,
        "iss": JWT_ISSUER,
        "iat": now,
        "exp": now + ACCESS_TOKEN_TTL_SECONDS,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

import time
import jwt

from app.service.auth.config import (
    JWT_SECRET,
    JWT_ISSUER,
    JWT_ALGORITHM,
    ACCESS_TOKEN_TTL_SECONDS,
)

INTERNAL_ACCESS_TOKEN_TTL_SECONDS = 300


def issue_access_token(user_id: str) -> str:
    now = int(time.time())

    payload = {
        "sub": user_id,
        "iss": JWT_ISSUER,
        "iat": now,
        "exp": now + ACCESS_TOKEN_TTL_SECONDS,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def issue_internal_access_token(user_id: str) -> tuple[str, int]:
    now = int(time.time())

    payload = {
        "sub": user_id,
        "iss": JWT_ISSUER,
        "iat": now,
        "exp": now + INTERNAL_ACCESS_TOKEN_TTL_SECONDS,
        "actor_type": "service",
        "actor_id": "ingestion-worker",
        "scope": "internal_impersonation",
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token, INTERNAL_ACCESS_TOKEN_TTL_SECONDS
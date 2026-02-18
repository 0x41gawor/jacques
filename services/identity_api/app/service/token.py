# app/service/token.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets

from app.service.auth.jwt import issue_access_token
from app.service.auth.crypto import hash_refresh_token
from app.service.auth.config import REFRESH_TOKEN_TTL_SECONDS, ACCESS_TOKEN_TTL_SECONDS


class TokenService:
    def __init__(self, *, refresh_repo):
        self._refresh_repo = refresh_repo

    def issue_tokens(self, *, user_id: str) -> dict:
        refresh_token = secrets.token_urlsafe(64)
        refresh_token_hash = hash_refresh_token(refresh_token)

        expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=REFRESH_TOKEN_TTL_SECONDS)

        self._refresh_repo.insert(
            user_id=user_id,
            token_hash=refresh_token_hash,
            expires_at=expires_at,
        )

        access_token = issue_access_token(user_id)

        return {
            "access_token": access_token,
            "access_token_expires_in": ACCESS_TOKEN_TTL_SECONDS,
            "refresh_token": refresh_token,
            "refresh_token_expires_in": REFRESH_TOKEN_TTL_SECONDS,
        }

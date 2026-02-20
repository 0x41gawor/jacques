# app/service/token.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets

from common.logging.trace import trace

from app.service.auth.jwt import issue_access_token
from app.service.auth.crypto import hash_refresh_token
from app.service.auth.config import REFRESH_TOKEN_TTL_SECONDS, ACCESS_TOKEN_TTL_SECONDS

from .exceptions import InvalidRefreshToken

class TokenService:
    def __init__(self, *, refresh_repo):
        self._refresh_repo = refresh_repo

    @trace
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

    @trace
    def refresh(self, *, refresh_token: str) -> dict:
        token_hash = hash_refresh_token(refresh_token)

        existing = self._refresh_repo.find_valid(token_hash=token_hash)

        if not existing:
            raise InvalidRefreshToken("invalid_or_expired_refresh_token")

        # 🔐 rotation (best practice)
        self._refresh_repo.revoke(token_hash=token_hash)

        # issue new refresh token
        new_refresh_token = secrets.token_urlsafe(64)
        new_hash = hash_refresh_token(new_refresh_token)

        expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=REFRESH_TOKEN_TTL_SECONDS)

        self._refresh_repo.insert(
            user_id=existing.user_id,
            token_hash=new_hash,
            expires_at=expires_at,
        )

        access_token = issue_access_token(str(existing.user_id))

        return {
            "access_token": access_token,
            "access_token_expires_in": ACCESS_TOKEN_TTL_SECONDS,
            "refresh_token": new_refresh_token,
            "refresh_token_expires_in": REFRESH_TOKEN_TTL_SECONDS,
        }

    @trace
    def logout(self, *, refresh_token: str) -> None:
        token_hash = hash_refresh_token(refresh_token)
        self._refresh_repo.revoke(token_hash=token_hash)
    
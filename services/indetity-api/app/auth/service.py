# auth/service.py
from datetime import datetime, timedelta, timezone

from auth.jwt import issue_access_token
from auth.crypto import hash_refresh_token
from auth.config import REFRESH_TOKEN_TTL_SECONDS, ACCESS_TOKEN_TTL_SECONDS
from repo.refresh_tokens import RefreshTokenRepository
import secrets


def issue_auth_tokens(*, user_id: str, db):
    refresh_repo = RefreshTokenRepository(db)

    refresh_token = secrets.token_urlsafe(64)
    refresh_token_hash = hash_refresh_token(refresh_token)

    expires_at = datetime.now(tz=timezone.utc) + timedelta(
        seconds=REFRESH_TOKEN_TTL_SECONDS
    )

    refresh_repo.insert(
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


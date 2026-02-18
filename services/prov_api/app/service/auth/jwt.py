from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID
import jwt

from app.service.auth.config import JWT_SECRET, JWT_ISSUER, JWT_ALGORITHM


class AuthError(Exception):
    """Base auth exception."""


class MissingBearerToken(AuthError):
    pass


class InvalidToken(AuthError):
    pass


@dataclass(frozen=True)
class AuthContext:
    user_id: UUID
    claims: dict


def parse_bearer_token(auth_header: str | None) -> str:
    if not auth_header:
        raise MissingBearerToken("missing_authorization_header")

    # Expected: "Bearer <token>"
    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise MissingBearerToken("invalid_authorization_header_format")

    return parts[1].strip()


def verify_access_token(token: str) -> AuthContext:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            options={
                "require": ["sub", "exp", "iat", "iss"],
            },
            leeway=10,  # sekundy tolerancji na clock skew
        )
    except jwt.ExpiredSignatureError as e:
        raise InvalidToken("token_expired") from e
    except jwt.InvalidIssuerError as e:
        raise InvalidToken("invalid_issuer") from e
    except jwt.InvalidTokenError as e:
        raise InvalidToken("invalid_token") from e

    sub = payload.get("sub")
    if not sub:
        raise InvalidToken("missing_sub")

    try:
        user_id = UUID(str(sub))
    except Exception as e:
        raise InvalidToken("sub_is_not_uuid") from e

    return AuthContext(user_id=user_id, claims=payload)

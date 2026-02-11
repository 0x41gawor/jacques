# app/service/oauth_callback.py
from __future__ import annotations

from app.service.exceptions import MissingOAuthCode
from app.service.google_oauth_client import GoogleOAuthClient


class OAuthCallbackService:
    def __init__(
        self,
        *,
        google_oauth: GoogleOAuthClient,
        user_service,
        token_service,
    ):
        self._google_oauth = google_oauth
        self._user_service = user_service
        self._token_service = token_service

    def handle_callback(self, *, code: str | None, state: str | None) -> dict:
        if not code or not state:
            raise MissingOAuthCode("missing code or state")

        idinfo = self._google_oauth.exchange_and_verify(code)

        google_id = idinfo["sub"]
        name = idinfo.get("name")

        user = self._user_service.create_or_find_user(
            google_id=google_id,
            name=name,
        )

        return self._token_service.issue_tokens(user_id=str(user.id))

# app/service/google_oauth_client.py
from __future__ import annotations

import os
import requests

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.service.exceptions import OAuthExchangeFailed, InvalidIdToken

class GoogleOAuthClientService:
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        token_url: str = "https://oauth2.googleapis.com/token",
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._token_url = token_url

    def exchange_and_verify(self, code: str) -> dict:
        token_response = self._exchange_code_for_tokens(code)

        id_token_str = token_response.get("id_token")
        if not id_token_str:
            raise OAuthExchangeFailed("missing_id_token")

        return self._verify_id_token(id_token_str)

    def _exchange_code_for_tokens(self, code: str) -> dict:
        payload = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self._redirect_uri,
        }

        try:
            response = requests.post(
                self._token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise OAuthExchangeFailed(str(e)) from e

    def _verify_id_token(self, id_token_str: str) -> dict:
        try:
            req = google_requests.Request()
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                req,
                self._client_id,
            )

            if idinfo.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
                raise InvalidIdToken("wrong_issuer")

            return idinfo
        except Exception as e:
            raise InvalidIdToken(str(e)) from e

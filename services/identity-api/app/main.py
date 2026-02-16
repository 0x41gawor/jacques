# app/main.py
from __future__ import annotations
import os
from dotenv import load_dotenv
import flask

load_dotenv()   

from app.db.executor import PostgresExecutor
from app.repo.users import UserRepository
from app.repo.refresh_tokens import RefreshTokenRepository
from app.repo.decks import DeckRepository


from app.service.google_oauth_client import GoogleOAuthClientService
from app.service.oauth_callback import OAuthCallbackService
from app.service.token import TokenService
from app.service.user import UserService

from app.http.auth_bp import create_auth_blueprint

def create_app():
    app = flask.Flask(__name__)

    # --- INFRA / CONFIG ---
    google_client_id = os.environ["OAUTH2_CLIENT_GOOGLE_CLIENT_ID"]
    google_client_secret = os.environ["OAUTH2_CLIENT_GOOGLE_CLIENT_SECRET"]
    redirect_uri = os.environ["OAUTH2_REDIRECT_URI"]

    db = PostgresExecutor()

    # --- REPOS ---
    user_repo = UserRepository(db=db)
    refresh_repo = RefreshTokenRepository(db=db)
    deck_repo = DeckRepository(db=db)

    # --- SERVICES ---
    google_oauth = GoogleOAuthClientService(
        client_id=google_client_id,
        client_secret=google_client_secret,
        redirect_uri=redirect_uri,
    )
    user_service = UserService(
        user_repo=user_repo,
        deck_repo=deck_repo,
    )
    token_service = TokenService(
        refresh_repo=refresh_repo
    )

    oauth_callback_service = OAuthCallbackService(
        google_oauth=google_oauth,
        user_service=user_service,
        token_service=token_service,
    )

    # --- HTTP ---
    auth_bp = create_auth_blueprint(oauth_callback_service=oauth_callback_service)
    app.register_blueprint(auth_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    port = os.environ.get("BANDARI")
    app.run(host="0.0.0.0", port=port, debug=True)

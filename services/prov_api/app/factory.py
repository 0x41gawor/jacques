import flask
import os

from common.db.executor import PostgresExecutor
from common.logging.http import register_request_logging
from common.health.flask import create_health_blueprint
from common.health.base import HealthRegistry
from common.health.database import DatabaseHealthCheck
from app.http.health import GeminiHealthCheck

from app.repo.decks import DeckRepository
from app.repo.flashcards import FlashcardRepository
from app.service.deck import DeckService

from app.http.prov import create_prov_blueprint
from app.service.flashcard_service import FlashcardService
from app.service.gemini_flashcard_generator import GeminiFlashcardGenerator

def create_app():
    app = flask.Flask(__name__)

    db = PostgresExecutor()

    deck_repo = DeckRepository(db=db)
    flashcard_repo = FlashcardRepository(db=db)

    deck_service = DeckService(deck_repo=deck_repo)

    flashcard_generator = GeminiFlashcardGenerator(
        google_ai_studio_api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY")
    )
    flashcard_service = FlashcardService(
        generator=flashcard_generator,
        deck_service=deck_service,
        flashcard_repo=flashcard_repo
    )

    # --- HTTP request logging ---
    register_request_logging(app)
    # --- HEALTH CHECKS ---
    health_registry = HealthRegistry()
    health_registry.register(DatabaseHealthCheck(db))
    health_registry.register(GeminiHealthCheck(flashcard_generator))
    app.register_blueprint(create_health_blueprint(registry=health_registry))
    # --- API BLUEPRINTS ---
    prov_bp = create_prov_blueprint(flashcard_service=flashcard_service)

    app.register_blueprint(prov_bp)

    return app
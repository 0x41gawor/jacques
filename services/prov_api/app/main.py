import os
from dotenv import load_dotenv
import flask

load_dotenv()

from common.logging.config import configure_logging
from common.logging.mixin import LoggingMixin
configure_logging()

from common.db.executor import PostgresExecutor

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

    prov_bp = create_prov_blueprint(flashcard_service=flashcard_service)
    app.register_blueprint(prov_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    port = os.environ.get("TOKARI")
    app.run(host="0.0.0.0", port=port, debug=True)
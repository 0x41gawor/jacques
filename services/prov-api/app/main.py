import os
from dotenv import load_dotenv
import flask

load_dotenv()

from app.http.prov import create_prov_blueprint
from app.service.flashcard_service import FlashcardService
from app.service.gemini_flashcard_generator import GeminiFlashcardGenerator


def create_app():
    app = flask.Flask(__name__)

    flashcard_generator = GeminiFlashcardGenerator(
        google_ai_studio_api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY")
    )
    flashcard_service = FlashcardService(generator=flashcard_generator)

    prov_bp = create_prov_blueprint(flashcard_service=flashcard_service)
    app.register_blueprint(prov_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    port = os.environ.get("TOKARI")
    app.run(host="0.0.0.0", port=port, debug=True)
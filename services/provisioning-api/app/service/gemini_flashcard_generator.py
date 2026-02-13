import json
import httpx
from typing import List

from app.protocols import FlashcardGenerator
from app.service.model.flashcard import Flashcard

from .config import SYSTEM_PROMPT


GEMINI_MODEL = "models/gemini-2.5-flash"
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"{GEMINI_MODEL}:generateContent"
)

class GeminiFlashcardGenerator(FlashcardGenerator):

    def __init__(self, google_ai_studio_api_key: str):
        self.api_key = google_ai_studio_api_key
        self.client = httpx.Client(timeout=30.0)

    def generate_flashcard(
        self,
        word: str,
        example: str | None = None,
        part: str | None = None,
    ) -> List[Flashcard]:

        user_payload = {
            "word": word,
        }

        if example:
            user_payload["example"] = example

        if part:
            user_payload["part"] = part

        body = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [{
                "role": "user",
                "parts": [{
                    "text": json.dumps(user_payload)
                }]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json",
                "maxOutputTokens": 2048,
            }
        }

        response = self.client.post(
            GEMINI_ENDPOINT,
            params={"key": self.api_key},
            json=body,
        )

        response.raise_for_status()

        data = response.json()

        try:
            raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError("Invalid Gemini response structure")

        try:
            flashcards_data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise RuntimeError("Gemini returned invalid JSON") from e

        return self._to_entities(flashcards_data)

    # -------------------------
    # internal mapping layer
    # -------------------------

    def _to_entities(self, flashcards_data: list[dict]) -> List[Flashcard]:
        return [Flashcard.from_dict(item) for item in flashcards_data]  

    def close(self):
        self.client.close()


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    generator = GeminiFlashcardGenerator(
        google_ai_studio_api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY")
    )
    flashcards = generator.generate_flashcard("serendipity", None, None)

    for card in flashcards:
        print(card)

    generator.close()
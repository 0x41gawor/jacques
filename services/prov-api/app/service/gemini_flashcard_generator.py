import json
from typing import Iterable
import httpx
import re

from app.protocols import FlashcardGenerator
from app.service.model.flashcard import Flashcard, FlashcardBuilder

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
    ) -> list[Flashcard]:

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

        return self._to_entities(flashcards_data, word)

    # -------------------------
    # internal mapping layer
    # -------------------------

    def _to_entities(self, flashcards_data: list[dict], word: str) -> list[Flashcard]:
        entities = []

        for item in flashcards_data:
            builder = FlashcardBuilder.from_json(item)
            builder.example_position = find_word_position(builder.example_sentence, [builder.word, word])
            builder.definition = capitalize_first_letter(builder.definition)
            builder.example_sentence = capitalize_first_letter(builder.example_sentence)
            entity = builder.build()
            entities.append(entity)

        return entities


    def close(self):
        self.client.close()



def normalize_token(token: str) -> str:
    return re.sub(r"[^\w'-]", "", token).lower()


def find_word_position(sentence: str, candidates: Iterable[str]) -> int:
    """
    Returns zero-based index of first matching candidate word/phrase.
    Supports multi-word expressions.
    Case-insensitive.
    Strips punctuation.
    """
    tokens = sentence.split()
    normalized_tokens = [normalize_token(t) for t in tokens]

    for candidate in candidates:
        # 🔥 rozszerzamy candidate o warianty
        expanded_forms = generate_past_forms(normalize_token(candidate))

        for form in expanded_forms:
            candidate_parts = form.split()
            n = len(candidate_parts)

            for i in range(len(normalized_tokens) - n + 1):
                if normalized_tokens[i:i+n] == candidate_parts:
                    return i

    raise ValueError(
        f"No candidate {list(candidates)} found in sentence: {sentence}"
    )


def capitalize_first_letter(s: str) -> str:
    if not s:
        return s
    return s[0].upper() + s[1:]

def generate_past_forms(word: str) -> list[str]:
    """
    Very simple regular past tense generator.
    Not linguistically complete — only pragmatic fallback.
    """

    if not word:
        return []

    forms = [word]

    # ends with 'e' → just add 'd'
    if word.endswith("e"):
        forms.append(word + "d")
    else:
        forms.append(word + "ed")

    # optional: consonant doubling heuristic (CVC)
    if (
        len(word) >= 3
        and word[-1] not in "aeiou"
        and word[-2] in "aeiou"
        and word[-3] not in "aeiou"
    ):
        forms.append(word + word[-1] + "ed")

    # optional: y → ied
    if word.endswith("y") and len(word) >= 2 and word[-2] not in "aeiou":
        forms.append(word[:-1] + "ied")

    return list(set(forms))



if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    generator = GeminiFlashcardGenerator(
        google_ai_studio_api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY")
    )
    flashcards = generator.generate_flashcard(word="pervades", example=None, part=None)

    for card in flashcards:
        print(card)

    generator.close()
from typing import Protocol
from app.service.model.flashcard import Flashcard

class FlashcardGenerator(Protocol):
    def generate_flashcard(self, word: str, example: str | None, part: str | None) -> list[Flashcard]:
        ...
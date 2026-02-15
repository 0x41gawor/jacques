from .model.flashcard import Flashcard
from app.protocols import FlashcardGenerator


class FlashcardService():
    def __init__(self, generator: FlashcardGenerator):
        self.generator = generator

    def create_flashcard(self, word: str, example: str | None, part: str | None) -> list[Flashcard]:
        flashcards = [] 
        try:
            flashcards = self.generator.generate_flashcard(word, example, part)
        except Exception as e:
            raise RuntimeError(f"Failed to create flashcard: {e}")
        return flashcards
from uuid import UUID
from .model.flashcard import Flashcard
from app.protocols import FlashcardGenerator

from app.service.deck import DeckService
from app.repo.flashcards import FlashcardRepository

class FlashcardService():
    def __init__(self, generator: FlashcardGenerator, deck_service: DeckService, flashcard_repo: FlashcardRepository):
        self.generator = generator
        self.deck_service = deck_service
        self.flashcard_repo = flashcard_repo

    def create_flashcard(self, user_id: UUID, word: str, example: str | None, part: str | None) -> list[Flashcard]:
        try:
            deck = self.deck_service.get_default_deck_by_user_id(user_id)
        except Exception:
            raise RuntimeError("Failed to get default deck for user")
        
        generated = [] 
        try:
            generated = self.generator.generate_flashcard(word.lower(), example, part)
        except Exception as e:
            raise RuntimeError(f"Failed to create flashcard: {e}")
        
        ids = []
        for fc in generated:
            new_id = self.flashcard_repo.insert(
                deck_id=deck.id,
                flashcard=fc,
            )
            # //TODO insert flashcard state here as well
            ids.append(new_id)

        return generated
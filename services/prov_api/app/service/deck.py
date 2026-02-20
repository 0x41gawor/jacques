from uuid import UUID

from common.logging.trace import trace
from app.repo.decks import DeckRepository
from app.repo.models import Deck


class DeckNotFound(Exception):
    pass


class DeckService:
    def __init__(self, *, deck_repo: DeckRepository):
        self._deck_repo = deck_repo

    @trace
    def get_default_deck_by_user_id(self, user_id: UUID) -> Deck:
        deck = self._deck_repo.find_default_by_user_id(user_id)

        if not deck:
            # to nie powinno się zdarzyć, bo identity-api powinno
            # tworzyć default deck przy rejestracji
            raise DeckNotFound(f"default deck not found for user {user_id}")

        return deck
    @trace
    def get_all_decks_by_user_id(self, user_id: UUID) -> list[Deck]:
        return self._deck_repo.find_by_user_id(user_id)

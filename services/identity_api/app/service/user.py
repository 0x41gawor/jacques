from __future__ import annotations

from common.logging.trace import trace

from app.repo.users import UserRepository
from app.repo.decks import DeckRepository


class UserService:
    def __init__(self, *, user_repo: UserRepository, deck_repo: DeckRepository):
        self._user_repo = user_repo
        self._deck_repo = deck_repo
    
    @trace
    def create_or_find_user(self, *, google_id: str, name: str | None):
        user = self._user_repo.find_by_google_id(google_id)
        if user:
            return user

        # 1️⃣ create user
        user = self._user_repo.create_user(google_id=google_id, name=name)

        # 2️⃣ create default deck (minimal contract)
        # //TODO move this operatiom to create_user and wrap in transaction
        self._deck_repo.insert_default(owner_id=user.id)

        return user
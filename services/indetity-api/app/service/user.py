# app/service/user.py
from __future__ import annotations


class UserService:
    def __init__(self, *, user_repo):
        self._user_repo = user_repo

    def create_or_find_user(self, *, google_id: str, name: str | None):
        user = self._user_repo.find_by_google_id(google_id)
        if user:
            return user
        return self._user_repo.create_user(google_id=google_id, name=name)

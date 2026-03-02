from typing import Protocol

class ExternalSourceService(Protocol):
    def fetch_words(self, date_from: str, date_to: str) -> list[str]:
        """Fetches a list of words from an external source."""
        ...
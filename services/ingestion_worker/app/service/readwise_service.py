import requests

from common.logging.mixin import LoggingMixin
from common.logging.trace import trace

from app.protocols import ExternalSourceService
from .utils import normalize_word


class ReadwiseService(LoggingMixin, ExternalSourceService):
    def __init__(self, readwise_url: str):
        self.readwise_url = readwise_url

    @trace
    def fetch_words(
        self,
        *,
        token: str,
        date_from: str,
        date_to: str,
    ) -> list[str]:
        page = 1
        headers = {"Authorization": f"Token {token}"}
        result: list[str] = []

        self.logger.info(
            "Starting Readwise fetch",
            extra={
                "date_from": date_from,
                "date_to": date_to,
            },
        )

        while True:
            params = {
                "page": page,
                "page_size": 1000,
                "updated_gt": date_from,
                "updated_lt": date_to,
            }

            r = requests.get(
                url=self.readwise_url,
                headers=headers,
                params=params,
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()

            results = data.get("results", [])
            if not results:
                break

            page_words = 0

            for h in results:
                raw_text = h.get("text")
                word = normalize_word(raw_text)

                if word:
                    result.append(word)
                    page_words += 1

            self.logger.info(
                "Processed Readwise page",
                extra={
                    "page": page,
                    "results_count": len(results),
                    "normalized_words_count": page_words,
                },
            )

            if not data.get("next"):
                break

            page += 1

        self.logger.info(
            "Finished Readwise fetch",
            extra={
                "total_words": len(result),
                "date_from": date_from,
                "date_to": date_to,
            },
        )

        return result
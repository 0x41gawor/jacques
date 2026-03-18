import requests

from common.logging.mixin import LoggingMixin
from common.logging.trace import trace


class ProvApiService(LoggingMixin):
    def __init__(self, prov_api_url: str):
        self._prov_api_url = prov_api_url

    @trace
    def generate_flashcard(self, *, token: str, word: str) -> None:
        self.logger.info(
            "Sending flashcard generation request to prov-api",
            extra={
                "word": word,
                "prov_api_url": self._prov_api_url,
            },
        )

        response = requests.post(
            self._prov_api_url,
            headers={
                "Authorization": f"Bearer {token}",
            },
            params={
                "word": word,
            },
            timeout=30,
        )

        if not response.ok:
            response_text = response.text[:2000]

            self.logger.error(
                "Prov-api returned error response",
                extra={
                    "word": word,
                    "status_code": response.status_code,
                    "response_text": response_text,
                },
            )

            try:
                response_json = response.json()
                self.logger.error(
                    "Prov-api error response JSON",
                    extra={
                        "word": word,
                        "status_code": response.status_code,
                        "response_json": response_json,
                    },
                )
            except Exception:
                pass

            response.raise_for_status()

        self.logger.info(
            "Flashcard generation request completed",
            extra={
                "word": word,
                "status_code": response.status_code,
            },
        )
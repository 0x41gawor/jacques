import requests

from common.logging.mixin import LoggingMixin
from common.logging.trace import trace


class ProvApiError(Exception):
    """Base class for prov-api related errors."""


class ProvApiUnauthorizedError(ProvApiError):
    """Raised when prov-api rejects the token/authentication."""


class ProvApiTransientError(ProvApiError):
    """Raised for retryable errors such as 429/5xx/timeouts."""


class ProvApiPermanentError(ProvApiError):
    """Raised for non-retryable client-side errors."""


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

        try:
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
        except requests.Timeout as e:
            self.logger.warning(
                "Prov-api request timed out",
                extra={"word": word},
            )
            raise ProvApiTransientError(f"prov-api timeout for word={word}") from e
        except requests.RequestException as e:
            self.logger.warning(
                "Prov-api request failed before response",
                extra={
                    "word": word,
                    "error": str(e),
                },
            )
            raise ProvApiTransientError(
                f"prov-api request exception for word={word}: {e}"
            ) from e

        if response.ok:
            self.logger.info(
                "Flashcard generation request completed",
                extra={
                    "word": word,
                    "status_code": response.status_code,
                },
            )
            return

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
            response_json = None

        status = response.status_code

        if status == 401:
            raise ProvApiUnauthorizedError(
                f"prov-api unauthorized for word={word}"
            )

        if status == 429 or 500 <= status <= 599:
            raise ProvApiTransientError(
                f"prov-api transient error for word={word}: status={status}"
            )

        raise ProvApiPermanentError(
            f"prov-api permanent error for word={word}: status={status}"
        )
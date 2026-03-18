import requests

from common.logging.mixin import LoggingMixin
from common.logging.trace import trace


class IdentityApiService(LoggingMixin):
    def __init__(self, base_url: str, internal_service_token: str):
        self._base_url = base_url.rstrip("/")
        self._internal_service_token = internal_service_token

    @trace
    def issue_user_token(self, *, user_id: str) -> str:
        self.logger.info(
            "Requesting user token from identity-api",
            extra={
                "user_id": user_id,
                "identity_api_base_url": self._base_url,
            },
        )

        response = requests.post(
            f"{self._base_url}/api/v1/internal/token",
            headers={
                "Authorization": f"Bearer {self._internal_service_token}",
                "Content-Type": "application/json",
            },
            json={"user_id": user_id},
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()

        self.logger.info(
            "User token issued successfully",
            extra={
                "user_id": user_id,
                "status_code": response.status_code,
            },
        )

        return data["access_token"]
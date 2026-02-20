
from common.health.base import HealthCheck


class GeminiHealthCheck(HealthCheck):
    name = "gemini"

    def __init__(self, client):
        self.client = client

    def check(self):
        try:
            self.client.ping()
            return {"status": "ok"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}
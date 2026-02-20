from .base import HealthCheck


class DatabaseHealthCheck(HealthCheck):
    name = "database"

    def __init__(self, db):
        self.db = db

    def check(self):
        try:
            self.db.execute("SELECT 1")
            return {"status": "ok"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}
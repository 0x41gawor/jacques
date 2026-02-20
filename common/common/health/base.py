from abc import ABC, abstractmethod
from typing import Dict


class HealthCheck(ABC):
    name: str

    @abstractmethod
    def check(self) -> Dict:
        """
        Returns:
            {
                "status": "ok" | "fail",
                "details": ...
            }
        """
        ...

# common/health/base.py

class HealthRegistry:
    def __init__(self):
        self._checks: list[HealthCheck] = []

    def register(self, check: HealthCheck):
        self._checks.append(check)

    def run(self) -> dict:
        results = {}
        overall_ok = True

        for check in self._checks:
            result = check.check()
            results[check.name] = result

            if result.get("status") != "ok":
                overall_ok = False

        return {
            "status": "ok" if overall_ok else "fail",
            "checks": results,
        }
from flask import Blueprint, jsonify
from .base import HealthRegistry


def create_health_blueprint(registry: HealthRegistry) -> Blueprint:
    bp = Blueprint("health", __name__, url_prefix="/health")

    @bp.route("/live", methods=["GET"])
    def live():
        return jsonify({"status": "ok"}), 200

    @bp.route("/ready", methods=["GET"])
    def ready():
        result = registry.run()

        status_code = 200 if result["status"] == "ok" else 503
        return jsonify(result), status_code

    return bp
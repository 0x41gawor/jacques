from flask import Blueprint, jsonify, request, g
from app.http.decorators import require_auth
def create_prov_blueprint(*, flashcard_service):
    prov_bp = Blueprint("prov", __name__, url_prefix="/flashcards")

    @prov_bp.route("/generate", methods=["POST"])
    @require_auth
    def create_flashcard():
        user_id = g.user_id  # UUID

        word = request.args.get("word")
        example = request.args.get("example")
        part = request.args.get("part")

        if not word:
            return jsonify({"error": "Missing required query param: word"}), 400

        try:
            flashcards = flashcard_service.create_flashcard(user_id, word, example, part)

            # na razie tylko “echo” w odpowiedzi, żebyś widział że działa
            return jsonify({
                "user_id": str(user_id),
                "flashcards": [fc.to_dict() for fc in flashcards],
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return prov_bp

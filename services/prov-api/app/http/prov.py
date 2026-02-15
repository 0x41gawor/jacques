

from flask import Blueprint, jsonify, request

def create_prov_blueprint(*, flashcard_service):
    prov_bp = Blueprint('prov', __name__, url_prefix='/prov')

    # //TODO GET dla Natki, żeby mogła z przeglądarki wejść :D Usunąć potem.
    @prov_bp.route('/flashcard', methods=['GET', 'POST'])
    def create_flashcard():
        word = request.args.get("word")
        example = request.args.get("example")
        part = request.args.get("part")

        if not word:
            return jsonify({"error": "Missing required query param: word"}), 400

        try:
            flashcards = flashcard_service.create_flashcard(word, example, part)
            return jsonify([flashcard.__dict__ for flashcard in flashcards]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return prov_bp
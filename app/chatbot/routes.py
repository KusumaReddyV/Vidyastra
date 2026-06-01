import logging

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import extensions
from app.ml_models.chatbot_engine import generate_chatbot_response, reset_mentor_session

logger = logging.getLogger(__name__)

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")


@chatbot_bp.route("/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json() or {}
    question = payload.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        answer = generate_chatbot_response(current_user.id, question)
        if extensions.mongo_db is not None:
            extensions.mongo_db.chatbot_history.insert_one(
                {"user_id": current_user.id, "question": question, "answer": answer}
            )
        return jsonify({"answer": answer})
    except Exception as exc:
        logger.error("Chatbot failed: %s", exc, exc_info=True)
        return jsonify({"error": "Mentor could not respond. Please try again."}), 500


@chatbot_bp.route("/reset", methods=["POST"])
@login_required
def reset():
    reset_mentor_session()
    return jsonify({"ok": True})

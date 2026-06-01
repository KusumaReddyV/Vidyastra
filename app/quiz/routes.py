import logging

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.db import get_user_quiz_results, save_quiz_result, save_quiz_session
from app.ml_models.quiz_engine import evaluate_quiz_submission, generate_adaptive_quiz

logger = logging.getLogger(__name__)

quiz_bp = Blueprint("quiz", __name__, url_prefix="/api/quiz")


@quiz_bp.route("/generate", methods=["POST"])
@login_required
def generate():
    data = request.get_json() or {}
    topic = (data.get("topic") or "python").strip() or "python"
    requested_difficulty = (data.get("difficulty", "adaptive") or "adaptive").lower()
    quiz_history = get_user_quiz_results(current_user.id)

    effective_difficulty = None
    if requested_difficulty != "adaptive":
        effective_difficulty = requested_difficulty

    try:
        quiz = generate_adaptive_quiz(
            current_user.id,
            topic,
            effective_difficulty,
            quiz_results=quiz_history,
        )
        quiz_id = save_quiz_session(
            {
                "user_id": current_user.id,
                "topic": quiz.get("topic", topic),
                "difficulty": quiz.get("difficulty", "easy"),
                "questions": quiz.get("questions", []),
                "score": None,
                "status": "in_progress",
            }
        )
        if quiz_id:
            quiz["quiz_id"] = quiz_id
        return jsonify(quiz)
    except Exception as exc:
        logger.error("Quiz generation failed: %s", exc, exc_info=True)
        return jsonify({"error": "Could not generate quiz. Please try another topic."}), 500


@quiz_bp.route("/submit", methods=["POST"])
@login_required
def submit():
    payload = request.get_json() or {}
    try:
        result = evaluate_quiz_submission(payload)
        result["user_id"] = current_user.id
        result["questions"] = payload.get("questions", [])
        result["difficulty"] = payload.get("difficulty") or result.get("difficulty")
        result["quiz_id"] = payload.get("quiz_id")
        result["status"] = "completed"
        quiz_id = save_quiz_result(result)
        if quiz_id:
            result["quiz_id"] = quiz_id
        return jsonify(result)
    except Exception as exc:
        logger.error("Quiz submit failed: %s", exc, exc_info=True)
        return jsonify({"error": "Failed to save quiz result. Please try again."}), 500

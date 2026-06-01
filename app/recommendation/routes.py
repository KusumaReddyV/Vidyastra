import logging

from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.db import get_student_profile, get_user_quiz_results
from app.ml_models.recommendation_engine import (
    build_career_roadmap,
    recommend_internships,
    recommend_learning_plan,
)

logger = logging.getLogger(__name__)

recommendation_bp = Blueprint("recommendation", __name__, url_prefix="/api/recommendation")


@recommendation_bp.route("/learning")
@login_required
def learning():
    profile = get_student_profile(current_user.id) or {}
    profile["user_id"] = current_user.id
    quiz_results = get_user_quiz_results(current_user.id)
    try:
        return jsonify(recommend_learning_plan(profile, quiz_results))
    except Exception as exc:
        logger.error("Learning recommendations failed: %s", exc, exc_info=True)
        return jsonify({"error": "Could not load recommendations."}), 500


@recommendation_bp.route("/internships")
@login_required
def internships():
    profile = get_student_profile(current_user.id) or {}
    profile["user_id"] = current_user.id
    try:
        return jsonify(recommend_internships(profile))
    except Exception as exc:
        logger.error("Internship recommendations failed: %s", exc, exc_info=True)
        return jsonify({"error": "Could not load opportunities."}), 500


@recommendation_bp.route("/roadmap")
@login_required
def roadmap():
    profile = get_student_profile(current_user.id) or {}
    profile["user_id"] = current_user.id
    try:
        return jsonify(build_career_roadmap(profile))
    except Exception as exc:
        logger.error("Career roadmap failed: %s", exc, exc_info=True)
        return jsonify({"error": "Could not load career roadmap."}), 500

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import extensions
from app.nlp_processor import NLPProcessor
from app.scoring_engine import ScoringEngine
from app.ml_models.resume_insights import analyze_resume_sections, grammar_score
from app.db import save_resume_version

resume_bp = Blueprint("resume", __name__, url_prefix="/api/resume")
nlp = NLPProcessor()
scorer = ScoringEngine()


@resume_bp.route("/enhanced-analysis", methods=["POST"])
@login_required
def enhanced_analysis():
    payload = request.get_json() or {}
    resume_text = payload.get("resume_text", "").strip()
    job_description = payload.get("job_description", "").strip()
    if not resume_text or not job_description:
        return jsonify({"error": "resume_text and job_description are required"}), 400

    resume_analysis = nlp.analyze_text(resume_text, text_type="resume")
    jd_analysis = nlp.analyze_text(job_description, text_type="job_description")
    score_data = scorer.calculate_job_fit_score(resume_analysis, jd_analysis)
    suggestions = scorer.generate_suggestions(resume_analysis, jd_analysis, score_data)

    missing = score_data.get("missing_keywords", [])
    section_health = analyze_resume_sections(resume_text)

    # Grammar scoring is independent of ATS score; combine later into a more realistic ATS estimate.
    g_score = grammar_score(resume_text)
    # Heuristic ATS improvement: grammar matters, but not more than job alignment.
    ats_score = int(score_data.get("overall_score", 0) * 0.85 + g_score * 0.15)
    response = {
        "ats_score": ats_score,
        "grammar_score": g_score,
        "missing_skills": missing,
        "resume_sections": section_health,
        "improvement_suggestions": suggestions,
        "certification_recommendations": [
            "Google Data Analytics",
            "AWS Cloud Practitioner",
            "Meta Front-End Professional Certificate",
        ],
        "project_recommendations": [
            "Portfolio website with deployment",
            "End-to-end ML mini project",
            "REST API with authentication",
        ],
        "career_suggestions": ["Apply to internships matching your top 5 skills."],
    }

    if extensions.mongo_db is not None:
        extensions.mongo_db.resumes.insert_one(
            {
                "user_id": current_user.id,
                "resume_text": resume_text[:2000],
                "job_description": job_description[:2000],
                "analysis": response,
            }
        )
        # Also store a full, versioned snapshot for history + learning.
        try:
            save_resume_version(
                current_user.id,
                {
                    "source": "enhanced_api",
                    "resume_text": resume_text,
                    "job_description": job_description,
                    "analysis": response,
                },
            )
        except Exception:
            pass
    return jsonify(response)

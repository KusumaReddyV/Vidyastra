import logging
from datetime import datetime

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

logger = logging.getLogger(__name__)
from flask_login import current_user, login_required
import json
from datetime import date

from app.db import (
    get_latest_resume_analysis,
    get_resume_history,
    get_student_profile,
    get_user_quiz_results,
    get_user_weak_subjects,
    upsert_weak_subjects,
    upsert_student_profile,
)
from app.ml_models.analytics_engine import build_dashboard_metrics
from app.services.activity_analytics import (
    build_activity_heatmap,
    compute_streaks,
    quiz_summary_stats,
)
from app.ml_models.resume_history_analyzer import build_resume_progress
from app.ml_models.weak_subject_model import detect_weak_subjects

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/vidyastra")
def landing():
    return render_template("index.html")


@dashboard_bp.route("/dashboard")
@dashboard_bp.route("/vidyastra/dashboard")
@login_required
def home():
    profile = get_student_profile(current_user.id) or {}
    settings = dict(profile.get("settings") or {})
    settings.setdefault("mentor_fab", True)
    quiz_results = get_user_quiz_results(current_user.id)
    weak_topics = detect_weak_subjects(quiz_results)
    # Persist weak topics for dashboard analytics.
    upsert_weak_subjects(current_user.id, weak_topics)

    weak_topics_db = get_user_weak_subjects(current_user.id)
    metrics = build_dashboard_metrics(quiz_results, weak_topics_db)
    latest_resume = get_latest_resume_analysis(current_user.id) or {}
    latest_analysis = latest_resume.get("analysis", {})

    upcoming_tasks = [f"Revise {w.get('topic')} for 30 minutes" for w in weak_topics_db[:3]]
    if not upcoming_tasks:
        upcoming_tasks = ["Take your first adaptive quiz to unlock personalized tasks."]

    recommended_actions = []
    missing_skills = latest_analysis.get("missing_skills", [])
    if missing_skills:
        recommended_actions.append(f"Add missing skills to resume: {', '.join(missing_skills[:3])}")
    if weak_topics_db:
        recommended_actions.append(f"Focus next quiz on {weak_topics_db[0].get('topic')}")
    if metrics.get("attempts", 0) < 3:
        recommended_actions.append("Complete 3 quizzes to improve recommendation quality.")
    try:
        from app.services.recommendation_service import build_dashboard_recommendations

        dash_reco = build_dashboard_recommendations(current_user.id, quiz_results)
        for step in dash_reco.get("next_steps", [])[:2]:
            if step not in recommended_actions:
                recommended_actions.insert(0, step)
        for gap in dash_reco.get("skill_gaps", [])[:2]:
            recommended_actions.append(f"Close skill gap: {gap}")
    except Exception:
        pass

    if not recommended_actions:
        recommended_actions = [
            "Take an adaptive quiz to unlock personalized recommendations",
            "Run Resume Analyzer to get ATS score insights",
            "Chat with Mentor for study guidance",
        ]

    activity_timeline = []
    for q in quiz_results[:5]:
        created = q.get("created_at")
        label = created.strftime("%d %b %Y") if hasattr(created, "strftime") else "Recent"
        activity_timeline.append(
            {
                "type": "quiz",
                "title": f"Quiz: {q.get('topic', 'general')} — {q.get('score', 0)}%",
                "meta": label,
                "icon": "fa-brain",
            }
        )
    resume_history = get_resume_history(current_user.id, limit=3)
    for r in resume_history:
        created = r.get("created_at")
        label = created.strftime("%d %b %Y") if hasattr(created, "strftime") else "Recent"
        score = (r.get("analysis") or {}).get("ats_score") or r.get("ats_score") or "—"
        activity_timeline.append(
            {
                "type": "resume",
                "title": f"Resume analyzed — ATS {score}%",
                "meta": label,
                "icon": "fa-file-lines",
            }
        )
    activity_timeline = activity_timeline[:8]

    recommendation_cards = [
        {"title": "Weak subject focus", "body": weak_topics_db[0].get("topic") if weak_topics_db else "Take quizzes to detect gaps", "href": url_for("dashboard.weak_subject_analysis"), "icon": "fa-triangle-exclamation"},
        {"title": "Career roadmap", "body": "Milestones tailored to your target role", "href": url_for("dashboard.career_roadmaps"), "icon": "fa-map"},
        {"title": "Study planner", "body": "Daily goals and revision reminders", "href": url_for("dashboard.study_planner"), "icon": "fa-calendar-check"},
    ]

    resume_history = get_resume_history(current_user.id, limit=40)
    heatmap = build_activity_heatmap(quiz_results, resume_history)
    streaks = compute_streaks(quiz_results)
    activity_stats = {
        "current_streak": streaks["current_streak"],
        "longest_streak": streaks["longest_streak"],
        "quizzes_solved": metrics.get("attempts", 0),
        "study_time_minutes": metrics.get("study_time_minutes", 0),
        "resume_score": latest_analysis.get("ats_score") or 0,
        "weekly_completion_pct": min(100, metrics.get("attempts", 0) * 14),
    }

    return render_template(
        "dashboard.html",
        profile=profile,
        quiz_results=quiz_results[:10],
        weak_topics=weak_topics_db,
        metrics=metrics,
        latest_ats=latest_analysis.get("ats_score", 0),
        quiz_accuracy=metrics.get("average_score", 0),
        learning_streak=max(streaks["current_streak"], 1) if streaks["current_streak"] else min(30, metrics.get("attempts", 0)),
        upcoming_tasks=upcoming_tasks,
        recommended_actions=recommended_actions,
        activity_timeline=activity_timeline,
        recommendation_cards=recommendation_cards,
        settings=settings,
        now_label=date.today().strftime("%A, %d %b %Y"),
        active_page="home",
        activity_heatmap_json=json.dumps(heatmap),
        activity_stats=activity_stats,
    )


@dashboard_bp.route("/dashboard/profile", methods=["GET", "POST"])
@dashboard_bp.route("/vidyastra/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        payload = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "department": request.form.get("department", "").strip(),
            "year": request.form.get("year", "").strip(),
            "skills": [s.strip() for s in request.form.get("skills", "").split(",") if s.strip()],
            "interests": [s.strip() for s in request.form.get("interests", "").split(",") if s.strip()],
            "cgpa": request.form.get("cgpa", "").strip(),
            "career_goals": request.form.get("career_goals", "").strip(),
            "learning_preferences": request.form.get("learning_preferences", "").strip(),
            "academic_history": request.form.get("academic_history", "").strip(),
            "profile_image_url": request.form.get("profile_image_url", "").strip(),
            "updated_on_label": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }
        upsert_student_profile(current_user.id, payload)

    profile_data = get_student_profile(current_user.id) or {}
    return render_template("vidyastra/profile.html", profile=profile_data, active_page="profile")


@dashboard_bp.route("/dashboard/weak-subject-analysis")
@login_required
def weak_subject_analysis():
    weak_topics = get_user_weak_subjects(current_user.id)
    weak_topics_json = json.dumps(
        [
            {
                "topic": w.get("topic"),
                "avg_score": w.get("avg_score", 0),
                "attempts": w.get("attempts", 0),
                "avg_time_spent_seconds": w.get("avg_time_spent_seconds", 0),
                "reasons": w.get("reasons", []),
            }
            for w in weak_topics
        ]
    )
    return render_template(
        "vidyastra/weak_subjects.html",
        active_page="weak",
        weak_topics=weak_topics,
        weak_topics_json=weak_topics_json,
    )


@dashboard_bp.route("/dashboard/resume-history")
@login_required
def resume_history():
    history = get_resume_history(current_user.id, limit=30)
    progress = build_resume_progress(history)
    return render_template(
        "vidyastra/resume_history.html",
        active_page="resume_history",
        progress=progress,
        progress_json=json.dumps(progress),
    )


@dashboard_bp.route("/dashboard/take-quiz")
@login_required
def take_quiz():
    return render_template("vidyastra/quiz_take.html")


@dashboard_bp.route("/dashboard/adaptive-quizzes")
@login_required
def adaptive_quizzes():
    quiz_results = get_user_quiz_results(current_user.id)
    profile = get_student_profile(current_user.id) or {}
    settings = dict(profile.get("settings") or {})
    settings.setdefault("default_quiz_topic", "python")
    # Pass sanitized JSON for client-side widgets.
    quiz_results_json = json.dumps(
        [
            {
                "topic": r.get("topic"),
                "score": r.get("score", 0),
                "created_at": (r.get("created_at").isoformat() if r.get("created_at") else None),
            }
            for r in quiz_results[:25]
        ]
    )
    return render_template(
        "vidyastra/quizzes.html",
        active_page="quiz",
        quiz_results=quiz_results,
        quiz_results_json=quiz_results_json,
        default_quiz_topic=settings.get("default_quiz_topic") or "python",
    )


@dashboard_bp.route("/dashboard/study-planner")
@login_required
def study_planner():
    return render_template("vidyastra/study_planner.html", active_page="study")


@dashboard_bp.route("/dashboard/learning-paths")
@login_required
def learning_paths_page():
    from app.services.data_loader import load_learning_paths
    from app.services.resume_intelligence import get_resume_profile

    profile = get_resume_profile(current_user.id)
    return render_template(
        "vidyastra/learning_paths.html",
        active_page="learning",
        paths=load_learning_paths(),
        career_goal=profile.get("career_goals") or "Software Engineer",
    )


@dashboard_bp.route("/api/study-plan", methods=["GET"])
@login_required
def api_study_plan():
    """Generate a personalized 7-day study plan from profile and quiz data."""
    from app.ml_models.study_planner_engine import generate_study_plan

    available_hours = request.args.get("hours", 2, type=int)
    try:
        plan = generate_study_plan(current_user.id, available_hours)
        return jsonify(plan)
    except Exception as exc:
        logger.error("Study plan failed: %s", exc, exc_info=True)
        return jsonify({"error": "Could not generate study plan."}), 500


@dashboard_bp.route("/dashboard/ai-recommendations")
@login_required
def ai_recommendations():
    return render_template("vidyastra/recommendations.html", active_page="recommend", initial_tab="learning")


@dashboard_bp.route("/dashboard/career-roadmaps")
@login_required
def career_roadmaps():
    return render_template("vidyastra/recommendations.html", active_page="roadmap", initial_tab="roadmap")


@dashboard_bp.route("/dashboard/internships")
@login_required
def internships():
    return render_template("vidyastra/recommendations.html", active_page="internships", initial_tab="internships")


@dashboard_bp.route("/dashboard/ai-mentor")
@login_required
def ai_mentor():
    return render_template("vidyastra/mentor.html", active_page="mentor")


@dashboard_bp.route("/dashboard/analytics")
@login_required
def analytics():
    quiz_results = get_user_quiz_results(current_user.id)
    weak_topics = get_user_weak_subjects(current_user.id)
    metrics = build_dashboard_metrics(quiz_results, weak_topics)
    quiz_results_json = json.dumps(
        [
            {
                "topic": r.get("topic", "general"),
                "score": r.get("score", 0),
                "time_spent_seconds": r.get("time_spent_seconds", 0),
                "created_at": (r.get("created_at").isoformat() if r.get("created_at") else None),
            }
            for r in quiz_results[:50]
        ]
    )
    resume_history = get_resume_history(current_user.id, limit=40)
    summary = quiz_summary_stats(quiz_results)
    streaks = compute_streaks(quiz_results)
    ats_trend = [
        (r.get("analysis") or {}).get("ats_score") or r.get("ats_score")
        for r in resume_history
        if (r.get("analysis") or {}).get("ats_score") or r.get("ats_score")
    ]
    ats_trend = [float(x) for x in ats_trend if x is not None][:12]

    analytics_data_json = json.dumps({
        "summary": summary,
        "streaks": streaks,
        "ats_trend": ats_trend,
        "heatmap": build_activity_heatmap(quiz_results, resume_history),
    })

    return render_template(
        "vidyastra/analytics.html",
        active_page="analytics",
        metrics=metrics,
        quiz_results_json=quiz_results_json,
        analytics_data_json=analytics_data_json,
        quiz_summary=summary,
        streaks=streaks,
    )


@dashboard_bp.route("/dashboard/settings", methods=["GET", "POST"])
@login_required
def settings():
    profile = get_student_profile(current_user.id) or {}
    settings_data = dict(profile.get("settings") or {})
    settings_data.setdefault("theme", "system")
    settings_data.setdefault("default_quiz_topic", "python")
    settings_data.setdefault("mentor_fab", True)

    if request.method == "POST":
        settings_data["theme"] = (request.form.get("theme") or "system").strip().lower()
        settings_data["default_quiz_topic"] = (request.form.get("default_quiz_topic") or "python").strip()
        settings_data["mentor_fab"] = bool(request.form.get("mentor_fab"))
        upsert_student_profile(current_user.id, {"settings": settings_data})
        return redirect(url_for("dashboard.settings"))

    return render_template("vidyastra/settings.html", active_page="settings", settings=settings_data)

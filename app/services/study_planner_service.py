"""Template-based study planner (no external API)."""

from typing import Any, Dict, List

from app.db import get_user_weak_subjects
from app.services.insight_writer import _pick, NEXT_STEP_OPENERS
from app.services.resume_intelligence import get_resume_profile
from app.utils import completed_quizzes


def generate_study_plan(user_id: str, available_hours_per_day: int = 2) -> Dict[str, Any]:
    profile = get_resume_profile(user_id)
    weak_subjects = get_user_weak_subjects(user_id, limit=5)
    weak_topics = [w.get("topic") for w in weak_subjects if w.get("topic")]
    from app.db import get_user_quiz_results

    quiz_results = get_user_quiz_results(user_id)
    completed = completed_quizzes(quiz_results)
    hours = max(1, min(6, int(available_hours_per_day or 2)))
    focus = weak_topics[0] if weak_topics else "DSA"
    goal = profile.get("career_goals") or "Software Engineer"

    daily_minutes = hours * 60
    week_plan = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    topics_rotation = weak_topics[:3] or ["python", "dsa", "dbms"]

    for i, day in enumerate(days):
        topic = topics_rotation[i % len(topics_rotation)]
        week_plan.append({
            "day": day,
            "focus": topic.upper() if len(topic) <= 5 else topic.title(),
            "duration_minutes": daily_minutes if i < 5 else max(30, daily_minutes // 2),
            "tasks": [
                f"Theory revision ({topic}) — {daily_minutes // 2} min",
                f"Practice quiz ({topic}) — {daily_minutes // 2} min",
            ],
        })

    return {
        "daily_goals": [
            f"{_pick(NEXT_STEP_OPENERS)} dedicating {hours} hours to **{focus}**, split between concept review and timed practice.",
            "After your quiz, spend ten minutes logging what each wrong answer had in common—that pattern is your real syllabus.",
            f"Given your goal of **{goal}**, ship one small portfolio improvement today (bullet, README, or deployment link).",
        ],
        "weekly_plan": week_plan,
        "revision_reminders": [
            {"time": "18:00", "message": f"Revise {focus} concepts"},
            {"time": "21:00", "message": "Review quiz mistakes from today"},
        ],
        "focus_areas": weak_topics[:5] or ["Fundamentals", "Problem solving"],
        "recommended_resources": [
            "Vidyastra adaptive quizzes",
            "Official documentation for your weakest topic",
            "Resume Analyzer for role-specific keywords",
        ],
        "study_tips": [
            "Use 25-minute focus blocks with 5-minute breaks",
            "Re-attempt questions you got wrong within 48 hours",
            "Track progress on your dashboard weekly",
        ],
        "weekly_summary": (
            f"This week centers on {', '.join(weak_topics[:3]) or focus} at roughly {hours}h/day, "
            f"building toward {goal} with quizzes plus one tangible resume or project win."
        ),
        "learning_streak_days": min(30, len(completed)),
        "weak_subjects": weak_topics,
    }

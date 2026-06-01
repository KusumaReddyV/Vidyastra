"""Resume-aware recommendations with narrative, insight-style copy."""

from typing import Any, Dict, List

from app.services.data_loader import load_career_paths, load_learning_paths
from app.services.insight_writer import (
    build_career_alignment,
    build_profile_highlights,
    build_project_recommendations,
    build_skill_growth_cards,
    build_suggested_improvements,
    narrative_dsa_readiness,
    narrative_deployment_gap,
    _pick,
    NEXT_STEP_OPENERS,
)
from app.services.resume_intelligence import analyze_skill_gaps, get_resume_profile
from app.utils import completed_quizzes, quiz_score, weak_topics_from_quizzes


def recommend_learning_plan(profile: Dict, quiz_results: List[Dict]) -> Dict[str, Any]:
    user_id = profile.get("user_id", "")
    resume = get_resume_profile(user_id) if user_id else profile
    gaps = analyze_skill_gaps(user_id) if user_id else analyze_skill_gaps_from_profile(resume)
    weak = weak_topics_from_quizzes(quiz_results)
    completed = completed_quizzes(quiz_results)
    streak = min(30, len(completed))
    goal = resume.get("career_goals") or profile.get("career_goals") or "Software Engineer"

    path_key = _learning_path_key(goal)
    paths = load_learning_paths()
    track = paths.get(path_key, paths.get("software_engineering", {}))

    daily = _narrative_daily_goals(resume, weak, gaps, goal)
    study_narrative = _study_plan_narrative(resume, track, goal, weak)

    return {
        "profile_highlights": build_profile_highlights(resume, gaps),
        "suggested_improvements": build_suggested_improvements(resume, gaps),
        "skill_growth": build_skill_growth_cards(resume, gaps),
        "recommended_projects": build_project_recommendations(resume),
        "career_alignment": build_career_alignment(resume),
        "daily_goals": daily,
        "weak_subjects": weak or gaps.get("missing_skills", [])[:5],
        "revision_reminders": _revision_reminders(weak, gaps),
        "course_recommendations": track.get("courses", []),
        "certification_recommendations": track.get("certifications", []),
        "learning_streak_days": streak,
        "badges": _badges(streak),
        "study_plan": study_narrative,
        "suggested_learning_path": track.get("phases", []),
        "skill_gaps": gaps.get("missing_skills", [])[:8],
        "resume_improvements": [i["body"] for i in build_suggested_improvements(resume, gaps)[:4]],
    }


def analyze_skill_gaps_from_profile(resume: Dict) -> Dict:
    """Lightweight gap pass when user_id unavailable."""
    uid = resume.get("user_id", "")
    if uid:
        return analyze_skill_gaps(uid)
    return {"missing_skills": [], "suggested_skills": [], "strengths": resume.get("skills", [])}


def recommend_internships(profile: Dict) -> Dict[str, Any]:
    resume = get_resume_profile(profile.get("user_id", "")) if profile.get("user_id") else profile
    skills = resume.get("skills", []) or profile.get("skills", [])
    goal = resume.get("career_goals") or "Software Engineer"
    from app.services.insight_writer import _join

    skill_str = _join(skills[:3]) if skills else "Python and problem solving"

    return {
        "internships": [
            {
                "title": "Software Engineering Intern",
                "company": "Product / SaaS company",
                "match_reason": (
                    f"Given your focus on {goal}, internships that emphasize shipping features "
                    f"and code review will complement your visible strengths in {skill_str}."
                ),
            },
            {
                "title": "Backend Development Intern",
                "company": "Startup or fintech",
                "match_reason": (
                    "Teams hiring for APIs and services value a deployed portfolio piece with tests, "
                    "README clarity, and observability basics—even at intern level."
                ),
            },
        ],
        "hackathons": [
            "Smart India Hackathon",
            "MLH Global Hack Week",
            "Devfolio online hackathons",
        ],
        "coding_contests": [
            "LeetCode Weekly Contest",
            "Codeforces Div 3",
            "CodeChef Starters",
        ],
        "projects": [
            p["body"][:120] + "…" if len(p.get("body", "")) > 120 else p.get("body", "")
            for p in build_project_recommendations(resume)
        ],
    }


def build_career_roadmap(profile: Dict) -> Dict[str, Any]:
    user_id = profile.get("user_id", "")
    resume = get_resume_profile(user_id) if user_id else profile
    goal = resume.get("career_goals") or profile.get("career_goals") or "Software Engineer"
    role_key = _career_role_key(goal)
    paths = load_career_paths()
    roadmap = paths.get(role_key, paths.get("software_engineer", {}))
    gaps = analyze_skill_gaps(user_id) if user_id else analyze_skill_gaps_from_profile(resume)

    narrative_intro = (
        f"Working toward **{roadmap.get('title', goal)}**, you're currently in the "
        f"**{roadmap.get('current_stage', 'foundation-building')}** phase. "
        f"A realistic horizon is **{roadmap.get('timeline', '6–12 months')}** with steady weekly practice."
    )

    steps = []
    for s in roadmap.get("steps", []):
        desc = s.get("description", "") if isinstance(s, dict) else ""
        title = s.get("title", s) if isinstance(s, dict) else str(s)
        steps.append({
            "title": title,
            "description": desc or f"Focus milestone {s.get('order', '')} on your roadmap.",
        })

    return {
        "target_role": roadmap.get("title", goal),
        "current_stage": roadmap.get("current_stage", "Building fundamentals"),
        "intro": narrative_intro,
        "steps": steps,
        "milestones": roadmap.get("milestones", []),
        "skills_to_acquire": gaps.get("missing_skills", [])[:8] or roadmap.get("skills_to_acquire", []),
        "projects_to_build": roadmap.get("projects_to_build", []),
        "interview_prep": roadmap.get("interview_prep", []),
        "timeline": roadmap.get("timeline", "6–12 months"),
    }


def build_dashboard_recommendations(user_id: str, quiz_results: List[Dict]) -> Dict[str, Any]:
    profile = get_resume_profile(user_id)
    profile["user_id"] = user_id
    plan = recommend_learning_plan(profile, quiz_results)
    return {
        "next_steps": plan["daily_goals"][:4],
        "skill_gaps": plan.get("skill_gaps", [])[:6],
        "resume_improvements": plan.get("resume_improvements", []),
        "focus_topic": weak_topics_from_quizzes(quiz_results)[:1] or plan.get("skill_gaps", [])[:1],
        "profile_highlights": plan.get("profile_highlights", [])[:2],
    }


def _narrative_daily_goals(resume: Dict, weak: List, gaps: Dict, goal: str) -> List[str]:
    goals = []
    if weak:
        goals.append(
            f"{_pick(NEXT_STEP_OPENERS)} a focused 45-minute block on **{weak[0]}**, "
            "then review one quiz attempt where that topic appeared."
        )
    elif gaps.get("missing_skills"):
        goals.append(
            f"To make your profile more placement-ready for **{goal}**, "
            f"study **{gaps['missing_skills'][0]}** with notes you can turn into a resume bullet."
        )
    tech = " ".join((resume.get("technologies") or [])).lower()
    if "flask" in tech and not any(x in tech for x in ("docker", "aws")):
        goals.append(narrative_deployment_gap(resume)[:200] + "…")
    goals.append(
        "Take one adaptive quiz, capture mistakes, and re-attempt missed concepts within 48 hours."
    )
    if len(goals) < 3:
        goals.append(narrative_dsa_readiness(resume, weak))
    return goals[:4]


def _study_plan_narrative(resume: Dict, track: Dict, goal: str, weak: List) -> str:
    base = track.get("summary", "")
    focus = weak[0] if weak else "core fundamentals"
    if base:
        return (
            f"{base} With your quiz history pointing at **{focus}**, prioritize that topic "
            f"in the next two weeks while keeping **{goal}** as your north star."
        )
    return (
        f"Your learning path toward **{goal}** should alternate deep work on **{focus}** "
        "with weekly portfolio improvements drawn from your resume gaps."
    )


def _revision_reminders(weak: List, gaps: Dict) -> List[Dict[str, str]]:
    topic = weak[0] if weak else (gaps.get("missing_skills") or ["fundamentals"])[0]
    return [
        {"time": "18:00", "message": f"Quick recall drill: {topic} definitions and one practice problem."},
        {"time": "21:00", "message": "Review today's quiz mistakes and write one sentence on each error pattern."},
    ]


def _badges(streak: int) -> List[Dict]:
    badges = []
    if streak >= 3:
        badges.append({"name": "Consistency", "description": "Multiple learning sessions logged recently."})
    if streak >= 7:
        badges.append({"name": "Weekly Momentum", "description": "A full week of steady practice."})
    return badges


def _learning_path_key(goal: str) -> str:
    g = goal.lower()
    if "data" in g:
        return "data_science"
    if "full stack" in g:
        return "full_stack"
    if "backend" in g:
        return "backend"
    if "front" in g:
        return "frontend"
    if "machine learning" in g or "ml" in g:
        return "machine_learning"
    return "software_engineering"


def _career_role_key(goal: str) -> str:
    g = goal.lower()
    if "data scientist" in g:
        return "data_scientist"
    if "full stack" in g:
        return "full_stack_developer"
    if "backend" in g:
        return "backend_engineer"
    return "software_engineer"

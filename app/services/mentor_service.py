"""Rule-based AI Mentor with session memory and resume personalization."""

import re
from typing import Any, Dict, List, Optional

from flask import session

from app.services.data_loader import load_mentor_knowledge
from app.services.insight_writer import _join, _pick, OPENERS, NEXT_STEP_OPENERS
from app.services.resume_intelligence import get_resume_profile

SESSION_KEY = "mentor_history"
MAX_HISTORY = 12


def _get_history() -> List[Dict[str, str]]:
    return list(session.get(SESSION_KEY, []))


def _append_history(role: str, content: str) -> None:
    history = _get_history()
    history.append({"role": role, "content": content})
    session[SESSION_KEY] = history[-MAX_HISTORY:]


def clear_history() -> None:
    session.pop(SESSION_KEY, None)


def _score_entry(question: str, entry: Dict[str, Any]) -> float:
    q = question.lower()
    score = 0.0
    for kw in entry.get("keywords", []):
        if kw.lower() in q:
            score += 2.0
    for pat in entry.get("question_patterns", []):
        if pat.lower() in q:
            score += 3.0
    for topic in entry.get("topics", []):
        if topic.lower() in q:
            score += 1.0
    return score


def _find_best_answer(question: str) -> Optional[Dict[str, Any]]:
    knowledge = load_mentor_knowledge()
    if not knowledge:
        return None
    ranked = sorted(knowledge, key=lambda e: _score_entry(question, e), reverse=True)
    if ranked and _score_entry(question, ranked[0]) > 0:
        return ranked[0]
    return ranked[0] if ranked else None


def _personalize(answer: str, resume: Dict[str, Any], question: str) -> str:
    parts = []
    skills = resume.get("skills") or resume.get("technologies") or []
    goal = resume.get("career_goals") or "your target role"

    if resume.get("has_resume") and skills:
        top = _join(skills, 4)
        parts.append(f"{_pick(OPENERS)} your profile already reflects strength in {top}.")
    elif not resume.get("has_resume"):
        parts.append(
            "Once you upload a resume in **Resume Analyzer**, I can tie guidance directly to your projects and skills."
        )

    parts.append(answer)

    steps = _action_steps(question, resume, skills, goal)
    if steps:
        parts.append("\n**Practical moves from here:**")
        parts.extend(f"- {s}" for s in steps)

    return "\n".join(parts)


def _action_steps(question: str, resume: Dict, skills: List[str], goal: str) -> List[str]:
    q = question.lower()
    steps = []
    if "resume" in q or "ats" in q:
        steps.extend([
            "Run Resume Analyzer against a target job description.",
            "Add measurable bullets (metrics, impact, technologies).",
            "Mirror keywords from the JD in your skills section.",
        ])
    elif "interview" in q or "placement" in q:
        steps.extend([
            "Practice 2 DSA problems daily on your weakest topic.",
            "Prepare 3 STAR stories from your projects.",
            f"Align talking points with your goal: {goal}.",
        ])
    elif "roadmap" in q or "plan" in q:
        weak = skills[0] if skills else "fundamentals"
        steps.extend([
            f"Block 45 minutes daily on {weak}.",
            "Complete one adaptive quiz per week and review mistakes.",
            "Ship one portfolio project in the next 30 days.",
        ])
    else:
        steps.extend([
            "A short adaptive quiz will surface which topics deserve your next study block.",
            "Align your profile goal with the roles you are targeting this season.",
            "Skim your **Resume Intelligence** panel for portfolio ideas tied to your stack.",
        ])
    return steps[:4]


def _contextual_followup(question: str, history: List[Dict[str, str]]) -> str:
    if len(history) < 2:
        return ""
    prev = history[-2].get("content", "").lower()
    if "resume" in prev and "interview" in question.lower():
        return "\n\nBuilding on your earlier question: strengthen resume keywords before interview outreach."
    return ""


def generate_mentor_response(user_id: str, question: str) -> str:
    question = (question or "").strip()
    if not question:
        return "Ask a specific question about skills, interviews, resume, or your career path."

    resume = get_resume_profile(user_id)
    history = _get_history()
    entry = _find_best_answer(question)

    if entry:
        base = entry.get("answer", "").strip()
    else:
        base = (
            "Focus on consistent practice: revise one core topic, take a timed quiz, "
            "and apply one improvement to your resume or portfolio this week."
        )

    response = _personalize(base, resume, question)
    response += _contextual_followup(question, history)

    _append_history("user", question)
    _append_history("assistant", response)
    return response

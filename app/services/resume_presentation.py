"""Structured resume analysis presentation for results UI."""

from typing import Any, Dict, List

from app.services.insight_writer import _join
from app.services.resume_intelligence import get_resume_profile


def enrich_analysis(results: Dict[str, Any], resume_text: str, user_id: str = "") -> Dict[str, Any]:
    """Attach recruiter-facing sections to analysis payload."""
    if user_id:
        profile = get_resume_profile(user_id)
        if resume_text and not profile.get("resume_text"):
            profile["resume_text"] = resume_text.lower()[:5000]
    else:
        profile = _profile_from_text(results, resume_text)
    profile["ats_score"] = results.get("overall_score")

    snapshot = {
        "name": profile.get("name") or "—",
        "degree": profile.get("degree") or profile.get("education") or "—",
        "skills": (results.get("resume_keywords") or profile.get("skills") or [])[:12],
        "tools": profile.get("technologies") or [],
        "projects": profile.get("project_titles") or profile.get("projects") or [],
        "technologies": profile.get("technologies") or [],
    }

    strengths = _strength_areas(profile, results)
    improvements = _improvement_suggestions(profile, results)
    ats_tips = _ats_tips(results)

    results["profile_snapshot"] = snapshot
    results["strength_areas"] = strengths
    results["improvement_suggestions"] = improvements
    results["ats_optimization_tips"] = ats_tips
    return results


def _profile_from_text(results: Dict, resume_text: str) -> Dict[str, Any]:
    from app.services.resume_intelligence import (
        _detect_certifications,
        _detect_projects,
        _detect_technologies,
        _extract_skills_from_text,
    )

    text = (resume_text or "").lower()
    skills = list(dict.fromkeys((results.get("resume_keywords") or []) + _extract_skills_from_text(text)))
    return {
        "skills": skills,
        "technologies": _detect_technologies(skills, text),
        "projects": _detect_projects(text),
        "project_titles": _extract_project_titles(resume_text),
        "certifications": _detect_certifications(text),
        "resume_text": text,
        "has_resume": bool(text),
    }


def _extract_project_titles(text: str) -> List[str]:
    titles = []
    if not text:
        return titles
    for line in text.splitlines():
        line = line.strip()
        if len(line) < 8 or len(line) > 80:
            continue
        lower = line.lower()
        if any(k in lower for k in ("project", "built", "developed", "application", "system")):
            if line[0].isupper() or line.startswith("•"):
                titles.append(line.lstrip("•- ").strip()[:70])
    return titles[:5]


def _strength_areas(profile: Dict, results: Dict) -> List[Dict[str, str]]:
    areas = []
    tech = profile.get("technologies") or []
    text = profile.get("resume_text", "")

    if any(t.lower() in ("flask", "django", "fastapi") for t in tech) or "flask" in text:
        areas.append({
            "title": "Backend Development",
            "detail": "Web framework experience is visible—position yourself for API and services roles.",
        })
    if "python" in " ".join(tech).lower() or "python" in text:
        areas.append({
            "title": "Python Programming",
            "detail": "Python appears across skills and project context—highlight libraries and outcomes.",
        })
    if "nlp" in text or "natural language" in text or "machine learning" in text:
        areas.append({
            "title": "NLP / ML Project Experience",
            "detail": "Intelligent-system projects differentiate you from generic web profiles.",
        })
    matched = results.get("matched_keywords") or []
    if len(matched) >= 5:
        areas.append({
            "title": "Role Keyword Overlap",
            "detail": f"Strong alignment on {_join(matched, 4)} relative to the job description.",
        })
    if not areas:
        areas.append({
            "title": "Foundational Profile",
            "detail": "Continue building project depth and measurable bullets to unlock stronger strength signals.",
        })
    return areas[:5]


def _improvement_suggestions(profile: Dict, results: Dict) -> List[str]:
    tips = []
    text = profile.get("resume_text", "")
    missing = results.get("missing_keywords") or []

    if not any(x in text for x in ("docker", "aws", "deploy", "render", "vercel")):
        tips.append("Add deployment experience (hosting URL, Docker, or cloud platform) to backend projects.")
    if "github" not in text.lower():
        tips.append("Add GitHub links beside each major project for quick verification.")
    if not any(ch.isdigit() for ch in text[:2500]):
        tips.append("Quantify project impact with metrics (users, % improvement, response time).")
    if missing:
        tips.append(
            f"Mirror high-priority JD terms in your skills section: {_join(missing, 4)}."
        )
    tips.append("Use action verbs (Built, Designed, Optimized) and consistent bullet formatting.")
    return tips[:6]


def _ats_tips(results: Dict) -> List[str]:
    tips = [
        "Group skills by category (Languages, Frameworks, Tools) for ATS parsing.",
        "Keep section headings standard: Education, Experience, Projects, Skills.",
        "Use one column layout where possible; avoid tables that parsers misread.",
    ]
    if results.get("overall_score", 0) < 70:
        tips.insert(0, "Increase keyword overlap by tailoring a version of this resume per application.")
    tips.append("Place the most relevant projects directly under skills matched to the job description.")
    return tips[:5]

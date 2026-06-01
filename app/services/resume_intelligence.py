"""Resume-derived profile and skill intelligence."""

import re
from typing import Any, Dict, List, Optional, Set

from app.db import get_latest_resume_analysis, get_student_profile
from app.services.data_loader import load_skill_gap_rules


def _normalize_skill(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _skill_set(items: List[str]) -> Set[str]:
    out = set()
    for item in items or []:
        n = _normalize_skill(item)
        if n:
            out.add(n)
    return out


def get_resume_profile(user_id: str) -> Dict[str, Any]:
    """Aggregate resume + student profile for recommendations."""
    profile = get_student_profile(user_id) or {}
    latest = get_latest_resume_analysis(user_id) or {}
    analysis = latest.get("analysis", {}) or {}

    resume_text = (latest.get("resume_text") or analysis.get("resume_text") or "").lower()
    skills = list(
        dict.fromkeys(
            (profile.get("skills") or [])
            + (analysis.get("resume_keywords") or analysis.get("matched_keywords") or [])
            + _extract_skills_from_text(resume_text)
        )
    )

    return {
        "name": profile.get("name") or analysis.get("name"),
        "email": profile.get("email"),
        "education": profile.get("academic_history") or profile.get("education") or "",
        "degree": profile.get("degree") or "",
        "department": profile.get("department") or "",
        "career_goals": profile.get("career_goals") or "Software Engineer",
        "skills": skills,
        "technologies": _detect_technologies(skills, resume_text),
        "projects": _detect_projects(resume_text),
        "project_titles": _extract_project_titles(resume_text),
        "domains": _infer_domains(resume_text, skills),
        "certifications": _detect_certifications(resume_text),
        "experience": analysis.get("experience_score"),
        "ats_score": analysis.get("ats_score") or analysis.get("overall_score"),
        "missing_skills": analysis.get("missing_skills") or analysis.get("missing_keywords") or [],
        "matched_skills": analysis.get("matched_keywords") or [],
        "resume_text": resume_text[:5000] if resume_text else "",
        "has_resume": bool(latest),
    }


def _extract_skills_from_text(text: str) -> List[str]:
    if not text:
        return []
    rules = load_skill_gap_rules()
    known = rules.get("known_skills", [])
    found = []
    for skill in known:
        if skill.lower() in text:
            found.append(skill)
    return found


def _detect_technologies(skills: List[str], text: str) -> List[str]:
    tech_keywords = [
        "python", "javascript", "java", "flask", "django", "react", "node",
        "mongodb", "sql", "mysql", "postgresql", "docker", "aws", "git",
        "html", "css", "nlp", "machine learning", "tensorflow", "pytorch",
    ]
    combined = _skill_set(skills) | set(re.findall(r"[a-z+#.]+", text))
    return [t for t in tech_keywords if t in " ".join(combined) or t in text]


def _extract_project_titles(text: str) -> List[str]:
    if not text:
        return []
    titles = []
    for line in text.splitlines():
        line = line.strip()
        if 8 <= len(line) <= 90 and (line[0].isupper() or line.startswith("•")):
            lower = line.lower()
            if any(k in lower for k in ("project", "built", "developed", "app", "system", "platform")):
                titles.append(line.lstrip("•- ").strip()[:80])
    return titles[:6]


def _infer_domains(text: str, skills: List[str]) -> List[str]:
    domains = []
    blob = " ".join(skills).lower() + " " + text
    mapping = [
        ("backend", ("flask", "django", "api", "rest", "microservice")),
        ("frontend", ("react", "javascript", "html", "css", "ui")),
        ("data", ("pandas", "sql", "analytics", "data science")),
        ("ml", ("machine learning", "nlp", "tensorflow", "pytorch")),
        ("devops", ("docker", "kubernetes", "aws", "ci/cd")),
    ]
    for name, keys in mapping:
        if any(k in blob for k in keys):
            domains.append(name.title())
    return domains


def _detect_projects(text: str) -> List[str]:
    if not text:
        return []
    projects = []
    for marker in ("project", "built", "developed", "implemented"):
        if marker in text:
            projects.append(marker)
            break
    if "flask" in text and "project" in text:
        projects.append("Flask application")
    if "nlp" in text or "resume" in text:
        projects.append("NLP / resume analysis")
    return projects[:5]


def _detect_certifications(text: str) -> List[str]:
    certs = []
    for c in ("aws certified", "google", "coursera", "udemy", "nptel", "oracle certified"):
        if c in text:
            certs.append(c.title())
    return certs


def analyze_skill_gaps(user_id: str) -> Dict[str, Any]:
    """Rule-based skill gap analysis from resume + target role."""
    resume = get_resume_profile(user_id)
    rules = load_skill_gap_rules()
    role = _normalize_role(resume.get("career_goals", ""))
    role_rules = rules.get("roles", {}).get(role, rules.get("roles", {}).get("software_engineer", {}))

    required = role_rules.get("required_skills", [])
    recommended = role_rules.get("recommended_skills", [])

    have = _skill_set(resume.get("skills", []))
    have |= _skill_set(resume.get("technologies", []))
    text = resume.get("resume_text", "")

    missing = []
    for skill in required:
        if not _has_skill(skill, have, text):
            missing.append(skill)

    suggestions = []
    for rule in rules.get("inference_rules", []):
        if _rule_matches(rule, have, text):
            for sug in rule.get("recommend", []):
                if not _has_skill(sug, have, text):
                    suggestions.append({"skill": sug, "reason": rule.get("reason", "")})

    for skill in recommended:
        if not _has_skill(skill, have, text) and skill not in missing:
            suggestions.append({"skill": skill, "reason": f"Recommended for {role.replace('_', ' ')}"})

    jd_missing = resume.get("missing_skills") or []
    for s in jd_missing[:8]:
        if s and s not in missing:
            missing.append(s)

    return {
        "target_role": role,
        "missing_skills": list(dict.fromkeys(missing))[:12],
        "suggested_skills": suggestions[:10],
        "strengths": list(have)[:15],
        "has_resume": resume.get("has_resume"),
    }


def _normalize_role(goal: str) -> str:
    g = goal.lower()
    if "data scientist" in g or "data science" in g:
        return "data_scientist"
    if "full stack" in g or "fullstack" in g:
        return "full_stack_developer"
    if "backend" in g:
        return "backend_engineer"
    if "frontend" in g or "front end" in g:
        return "frontend_developer"
    return "software_engineer"


def _has_skill(skill: str, have: Set[str], text: str) -> bool:
    s = _normalize_skill(skill)
    if s in have:
        return True
    return s in text


def _rule_matches(rule: Dict, have: Set[str], text: str) -> bool:
    if rule.get("has_any"):
        if not any(_has_skill(x, have, text) for x in rule["has_any"]):
            return False
    if rule.get("lacks_any"):
        if not any(not _has_skill(x, have, text) for x in rule["lacks_any"]):
            return False
    if rule.get("text_contains"):
        if not any(t in text for t in rule["text_contains"]):
            return False
    return True

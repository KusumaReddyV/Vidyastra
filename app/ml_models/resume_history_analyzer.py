"""
Analyze versioned resume uploads to surface trends and personalized insights.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Set


def _ats_from_analysis(analysis: Dict) -> int:
    if not analysis:
        return 0
    if "ats_score" in analysis:
        return int(analysis.get("ats_score") or 0)
    return int(analysis.get("overall_score") or 0)


def _skills_from_analysis(analysis: Dict) -> Set[str]:
    skills: Set[str] = set()
    if not analysis:
        return skills
    for key in ("matched_skills", "matched_keywords"):
        for s in analysis.get(key) or []:
            if s:
                skills.add(str(s).lower().strip())
    return skills


def _missing_from_analysis(analysis: Dict) -> Set[str]:
    missing: Set[str] = set()
    if not analysis:
        return missing
    for key in ("missing_skills", "missing_keywords"):
        for s in analysis.get(key) or []:
            if s:
                missing.add(str(s).lower().strip())
    return missing


def _infer_specialization(all_skills: Set[str], resume_text: str) -> str:
    text = (resume_text or "").lower()
    skills = " ".join(all_skills)
    combined = f"{text} {skills}"
    rules = [
        ("AI/ML", ["machine learning", "deep learning", "pytorch", "tensorflow", "nlp", "computer vision"]),
        ("Data Science", ["pandas", "statistics", "data analysis", "tableau", "power bi", "sql"]),
        ("Cloud/DevOps", ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd"]),
        ("Web Development", ["react", "javascript", "node", "html", "css", "frontend", "backend", "flask", "django"]),
        ("Mobile Development", ["android", "ios", "swift", "kotlin", "flutter", "react native"]),
    ]
    scores = []
    for label, keywords in rules:
        hit = sum(1 for k in keywords if k in combined)
        if hit:
            scores.append((hit, label))
    if not scores:
        return "General Software"
    scores.sort(reverse=True)
    return scores[0][1]


def build_resume_progress(history: List[Dict]) -> Dict[str, Any]:
    """
    Build resume progress analytics from newest-first history list.
    """
    if not history:
        return {
            "versions": [],
            "ats_trend": [],
            "skills_added": [],
            "missing_reduced": [],
            "specialization": None,
            "completeness_score": 0,
            "recommendations": [
                "Upload your first resume in Resume Analyzer to start tracking ATS progress.",
            ],
            "keyword_coverage_pct": 0,
        }

    # Oldest -> newest for trends
    ordered = list(reversed(history))
    versions_out = []
    ats_trend = []
    all_skills: Set[str] = set()
    all_text = ""

    for idx, doc in enumerate(ordered, start=1):
        analysis = doc.get("analysis") or {}
        ats = _ats_from_analysis(analysis)
        created = doc.get("created_at")
        label = created.strftime("%Y-%m-%d") if hasattr(created, "strftime") else f"v{idx}"
        versions_out.append(
            {
                "version": idx,
                "label": label,
                "ats_score": ats,
                "source": doc.get("source", "upload"),
                "grammar_score": analysis.get("grammar_score"),
            }
        )
        ats_trend.append({"label": label, "score": ats})
        all_skills |= _skills_from_analysis(analysis)
        all_text += " " + (doc.get("resume_text") or "")[:5000]

    first_analysis = ordered[0].get("analysis") or {}
    last_analysis = ordered[-1].get("analysis") or {}
    first_missing = _missing_from_analysis(first_analysis)
    last_missing = _missing_from_analysis(last_analysis)
    first_skills = _skills_from_analysis(first_analysis)
    last_skills = _skills_from_analysis(last_analysis)

    skills_added = sorted(last_skills - first_skills)
    missing_reduced = sorted(first_missing - last_missing)

    # Keyword coverage: matched / (matched + missing) on latest
    latest_matched = _skills_from_analysis(last_analysis)
    latest_missing = _missing_from_analysis(last_analysis)
    denom = len(latest_matched) + len(latest_missing)
    keyword_coverage = round((len(latest_matched) / denom) * 100, 1) if denom else 0

    sections = last_analysis.get("resume_sections") or {}
    section_count = len(sections)
    good_sections = sum(1 for v in sections.values() if str(v).lower() == "good")
    completeness = round((good_sections / section_count) * 100) if section_count else 50

    specialization = _infer_specialization(all_skills, all_text)

    recommendations: List[str] = []
    if latest_missing:
        recommendations.append(f"Add high-impact keywords: {', '.join(list(latest_missing)[:5])}.")
    if len(ordered) >= 2 and ats_trend[-1]["score"] > ats_trend[0]["score"]:
        recommendations.append(
            f"Great progress — ATS improved by {ats_trend[-1]['score'] - ats_trend[0]['score']} points across uploads."
        )
    elif len(ordered) >= 2 and ats_trend[-1]["score"] < ats_trend[0]["score"]:
        recommendations.append("Latest ATS dipped — re-align resume keywords with your target job description.")
    recommendations.append(f"Based on your history, consider focusing on {specialization} roles and projects.")
    if completeness < 80:
        recommendations.append("Strengthen resume sections marked as “Improve” (projects, skills, certifications).")

    return {
        "versions": list(reversed(versions_out)),  # newest first for UI
        "ats_trend": ats_trend,
        "skills_added": skills_added[:12],
        "missing_reduced": missing_reduced[:12],
        "specialization": specialization,
        "completeness_score": completeness,
        "keyword_coverage_pct": keyword_coverage,
        "recommendations": recommendations[:6],
        "latest_ats": ats_trend[-1]["score"] if ats_trend else 0,
        "first_ats": ats_trend[0]["score"] if ats_trend else 0,
    }

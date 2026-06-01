"""Natural-language insight generation from resume NLP signals (no external LLM)."""

import random
from typing import Any, Dict, List, Optional


def _join(items: List[str], limit: int = 4) -> str:
    items = [s for s in items if s][:limit]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _pick(options: List[str]) -> str:
    return random.choice(options) if options else ""


OPENERS = [
    "Based on the technologies already present in your resume,",
    "Given your current projects and skill signals,",
    "From what your resume communicates today,",
    "Looking at your practical project exposure,",
    "Your profile suggests",
]

NEXT_STEP_OPENERS = [
    "A valuable next step would be",
    "One area that could strengthen this profile is",
    "To make your profile more placement-ready, consider",
    "Recruiters reviewing similar profiles often respond well when you",
]


def narrative_skill_growth(skill: str, reason: str = "", resume: Optional[Dict] = None) -> str:
    tech = _join((resume or {}).get("technologies", []) or (resume or {}).get("skills", []))
    opener = _pick(OPENERS)
    if reason:
        return f"{opener} {reason.lower().rstrip('.')}. Building depth in **{skill}** would round out your stack nicely."
    if tech:
        return (
            f"{opener} you show momentum with {tech}. "
            f"Deepening **{skill}** would add a complementary dimension recruiters expect for your target role."
        )
    return f"{_pick(NEXT_STEP_OPENERS)} investing focused practice in **{skill}** over the next few weeks."


def narrative_deployment_gap(resume: Dict) -> str:
    projects = resume.get("project_titles") or resume.get("projects") or []
    proj = _join(projects if isinstance(projects[0], str) else [str(p) for p in projects], 2)
    stack = _join([t for t in resume.get("technologies", []) if t.lower() in ("flask", "python", "django")])
    if stack and proj:
        return (
            f"Your resume shows strong experience with {stack} through work like {proj}. "
            "Strengthening deployment skills—such as Docker, cloud hosting, or CI/CD—would make this profile "
            "more complete for backend or full-stack roles."
        )
    if stack:
        return (
            f"Your resume highlights practical {stack} development. "
            "Adding a deployed, documented API or web app (Render, AWS, or Docker) would signal production readiness."
        )
    return (
        "Project sections read well technically; pairing them with deployment links and environment details "
        "helps recruiters trust that you can ship beyond localhost."
    )


def narrative_frontend_balance(resume: Dict) -> str:
    backend = [t for t in resume.get("technologies", []) if t.lower() in ("flask", "python", "django", "java")]
    if backend and "react" not in " ".join(resume.get("technologies", [])).lower():
        return (
            "Your project experience reflects solid backend development exposure. "
            "Adding one frontend-focused project using React or modern JavaScript could create stronger portfolio balance."
        )
    return (
        "A portfolio that shows both API design and a polished UI layer often stands out in full-stack screenings."
    )


def narrative_dsa_readiness(resume: Dict, weak_topics: List[str]) -> str:
    langs = _join([s for s in resume.get("skills", []) if s.lower() in ("python", "java", "c++")])
    weak = weak_topics[0] if weak_topics else "problem solving"
    if langs:
        return (
            f"You already demonstrate {langs} proficiency through project work. "
            f"Deepening data structures and algorithm practice—especially around {weak}—would strengthen placement readiness."
        )
    return (
        "Consistent timed practice on core DSA patterns (arrays, trees, graphs) will complement your project narrative in technical interviews."
    )


def narrative_strength_area(domain: str, evidence: str) -> str:
    return f"**{domain}** — {evidence}"


def build_profile_highlights(resume: Dict, gaps: Dict) -> List[str]:
    highlights = []
    tech = resume.get("technologies") or []
    skills = resume.get("skills") or []
    projects = resume.get("project_titles") or resume.get("projects") or []
    certs = resume.get("certifications") or []

    if tech:
        highlights.append(
            f"Technical footprint spans {_join(tech, 5)}—a credible foundation for hands-on engineering roles."
        )
    if projects:
        p = _join(projects if isinstance(projects[0], str) else [str(x) for x in projects], 3)
        highlights.append(f"Project work—including signals around {p}—shows applied development beyond coursework.")
    if resume.get("degree") or resume.get("education"):
        edu = resume.get("degree") or resume.get("education")
        highlights.append(f"Academic background ({edu}) supports your eligibility narrative for campus and early-career pipelines.")
    if certs:
        highlights.append(f"Certifications such as {_join(certs, 2)} add third-party validation to your skill claims.")
    if resume.get("ats_score") and resume["ats_score"] >= 75:
        highlights.append(
            f"ATS alignment is relatively strong ({resume['ats_score']}%), indicating good keyword overlap with target roles."
        )
    strengths = gaps.get("strengths") or []
    if strengths and len(highlights) < 4:
        highlights.append(
            f"Recurring strengths in your extracted profile include {_join(strengths[:6], 4)}."
        )
    if not highlights:
        highlights.append(
            "Upload a detailed resume and run analysis against a job description to unlock richer, role-specific highlights."
        )
    return highlights[:5]


def build_suggested_improvements(resume: Dict, gaps: Dict) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    text = resume.get("resume_text", "")

    if resume.get("ats_score") and resume["ats_score"] < 70:
        items.append({
            "title": "Strengthen ATS alignment",
            "body": (
                "Keyword overlap with the job description can be improved. Mirror required skills in a dedicated "
                "Skills section and weave the same terms into project bullets—without keyword stuffing."
            ),
            "badge": "ATS",
            "cta": "Improve Resume",
            "href": "/resume-analyzer",
        })

    if "github" not in text and "gitlab" not in text:
        items.append({
            "title": "Make work easy to verify",
            "body": (
                "Adding GitHub (or GitLab) links beside projects helps recruiters validate your code quickly—often "
                "the difference between a skim and a shortlist."
            ),
            "badge": "Portfolio",
            "cta": "Add GitHub links",
            "href": "/dashboard/ai-mentor",
        })

    if not any(ch.isdigit() for ch in text[:2000]):
        items.append({
            "title": "Quantify impact",
            "body": (
                "Where possible, attach metrics: users served, latency improved, accuracy gained, or team size. "
                "Numbers make project bullets memorable in a six-second resume scan."
            ),
            "badge": "Impact",
            "cta": "Improve Resume",
            "href": "/resume-analyzer",
        })

    for sug in (gaps.get("suggested_skills") or [])[:3]:
        skill = sug.get("skill") if isinstance(sug, dict) else str(sug)
        reason = sug.get("reason", "") if isinstance(sug, dict) else ""
        items.append({
            "title": f"Develop {skill}",
            "body": narrative_skill_growth(skill, reason, resume),
            "badge": "Growth",
            "cta": f"Explore {skill.split()[0]}",
            "href": "/dashboard/learning-paths",
        })

    for m in (gaps.get("missing_skills") or [])[:2]:
        if not any(m.lower() in (i.get("title") or "").lower() for i in items):
            items.append({
                "title": f"Build credibility in {m}",
                "body": (
                    f"For your target role, {m} appears underrepresented relative to typical shortlists. "
                    f"A short course plus one portfolio bullet referencing {m} can close that perception gap."
                ),
                "badge": "Role fit",
                "cta": "Practice DSA" if "dsa" in m.lower() else "Learning Paths",
                "href": "/dashboard/adaptive-quizzes" if "dsa" in m.lower() else "/dashboard/learning-paths",
            })

    return items[:6]


def build_skill_growth_cards(resume: Dict, gaps: Dict) -> List[Dict[str, Any]]:
    cards = []
    tech_set = " ".join((resume.get("technologies") or [])).lower()
    if "flask" in tech_set or "django" in tech_set:
        if not any(x in tech_set for x in ("docker", "aws", "deploy", "ci/cd")):
            cards.append({
                "title": "Cloud & deployment",
                "body": narrative_deployment_gap(resume),
                "badge": "DevOps",
                "cta": "Explore deployment",
            })
    if "javascript" in tech_set and "react" not in tech_set:
        cards.append({
            "title": "Modern frontend",
            "body": narrative_frontend_balance(resume),
            "badge": "Frontend",
            "cta": "Explore React",
        })
    if "nlp" in tech_set or "machine learning" in tech_set:
        if "transformers" not in tech_set:
            cards.append({
                "title": "NLP depth",
                "body": (
                    "Your resume signals NLP or ML-oriented work. Familiarity with Transformers, HuggingFace, "
                    "or structured evaluation would position those projects closer to industry ML pipelines."
                ),
                "badge": "ML",
                "cta": "ML learning path",
            })
    for sug in (gaps.get("suggested_skills") or [])[:4]:
        if len(cards) >= 5:
            break
        skill = sug.get("skill") if isinstance(sug, dict) else str(sug)
        cards.append({
            "title": skill,
            "body": narrative_skill_growth(skill, sug.get("reason", "") if isinstance(sug, dict) else "", resume),
            "badge": "Suggested",
            "cta": "Start learning",
        })
    return cards[:5]


def build_project_recommendations(resume: Dict) -> List[Dict[str, Any]]:
    recs = []
    tech = resume.get("technologies") or []
    goal = (resume.get("career_goals") or "software engineering").lower()

    if any(t.lower() == "flask" for t in tech):
        recs.append({
            "title": "Production-ready API",
            "body": (
                "Extend your Flask experience with authentication, tests, OpenAPI docs, and a Dockerized deploy—"
                "a concise story for backend interviews."
            ),
            "badge": "Project",
            "cta": "Build Full Stack Project",
        })
    if "react" not in " ".join(tech).lower() and "full stack" in goal:
        recs.append({
            "title": "Full-stack showcase",
            "body": (
                "Pair your existing backend work with a React dashboard (charts, auth, responsive layout) "
                "to demonstrate end-to-end ownership."
            ),
            "badge": "Portfolio",
            "cta": "Build Full Stack Project",
        })
    if not recs:
        recs.append({
            "title": "Flagship portfolio app",
            "body": (
                "Ship one well-documented project with README screenshots, clear setup steps, and a live demo URL—"
                "recruiters prioritize proof of execution."
            ),
            "badge": "Portfolio",
            "cta": "Resume Analyzer",
        })
    return recs[:4]


def build_career_alignment(resume: Dict) -> List[Dict[str, Any]]:
    goal = resume.get("career_goals") or "Software Engineer"
    tech = _join(resume.get("technologies", []) or resume.get("skills", []), 5)
    alignments = [
        {
            "role": goal,
            "body": (
                f"Your current stack ({tech or 'emerging profile'}) aligns with {goal} pipelines—"
                "emphasize project outcomes and stack keywords in each application."
            ),
            "match": "Primary target",
        }
    ]
    g = goal.lower()
    if "engineer" in g and "data" not in g:
        if any(t.lower() in ("python", "flask") for t in (resume.get("technologies") or [])):
            alignments.append({
                "role": "Backend Engineer",
                "body": "Python/Flask signals map cleanly to backend internships—highlight API design and data modeling.",
                "match": "Strong fit",
            })
    if "data" in g or any("ml" in str(t).lower() for t in (resume.get("skills") or [])):
        alignments.append({
            "role": "Data Analyst / ML Engineer",
            "body": "Lean into notebooks, metrics, and reproducible pipelines in project descriptions.",
            "match": "Adjacent path",
        })
    return alignments[:3]

import re
from typing import Dict, List


SECTION_HEADINGS = {
    "summary": ["summary", "professional summary", "objective", "profile"],
    "skills": ["skills", "technical skills", "core skills", "toolbox"],
    "experience": ["experience", "work experience", "employment", "professional experience"],
    "projects": ["projects", "project", "personal projects", "portfolio"],
    "education": ["education", "academics", "academic background", "qualifications"],
    "certifications": ["certifications", "certification", "licenses", "courses"],
}


def analyze_resume_sections(text: str) -> Dict[str, str]:
    """
    Lightweight resume section analysis using heading heuristics.
    Returns statuses for common resume sections.
    """
    if not text:
        return {}

    lowered = text.lower()
    statuses: Dict[str, str] = {}
    for section, variants in SECTION_HEADINGS.items():
        found = any(v in lowered for v in variants)
        # Also check if heading appears as a line prefix.
        line_hits = 0
        for v in variants:
            pattern = r"(?m)^[\\s\\t\\-]*" + re.escape(v) + r"\\b"
            if re.search(pattern, text, flags=re.IGNORECASE):
                line_hits += 1
        if found or line_hits > 0:
            statuses[section] = "Good"
        else:
            statuses[section] = "Improve"
    return statuses


def grammar_score(text: str) -> int:
    """
    Best-effort grammar scoring.
    Uses language-tool-python if available, otherwise falls back to heuristics.
    """
    if not text:
        return 0

    # Limit for performance.
    sample = text[:4000]

    try:
        import language_tool_python  # Lazy optional dependency

        tool = language_tool_python.LanguageTool("en-US")
        matches = tool.check(sample)
        # Map error count to a 0-100 score.
        errors = len(matches)
        score = 100 - min(70, errors * 2.0)
        return max(0, int(score))
    except Exception:
        # Heuristic fallback: penalize double spaces and common repeated tokens.
        doubled_spaces = len(re.findall(r"\s{2,}", sample))
        repeated_the = len(re.findall(r"\bthe\s+the\b", sample.lower()))
        repeated_and = len(re.findall(r"\band\s+and\b", sample.lower()))
        errors = doubled_spaces + repeated_the + repeated_and
        score = 88 - errors * 2
        return max(0, int(score))


def extract_missing_headings(resume_text: str) -> List[str]:
    sections = analyze_resume_sections(resume_text)
    missing = [k for k, v in sections.items() if v == "Improve"]
    return missing


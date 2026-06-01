"""Learning activity heatmap and analytics aggregates."""

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional


def _to_date(value) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None
    return None


def build_activity_heatmap(
    quiz_results: List[Dict],
    resume_events: Optional[List[Dict]] = None,
    days: int = 371,
) -> Dict[str, Any]:
    """GitHub-style daily activity counts for the last ~52 weeks."""
    end = date.today()
    start = end - timedelta(days=days - 1)
    counts: Dict[str, int] = defaultdict(int)

    for q in quiz_results or []:
        d = _to_date(q.get("created_at") or q.get("attempt_date"))
        if d and start <= d <= end:
            counts[d.isoformat()] += 2 if q.get("score") is not None else 1

    for r in resume_events or []:
        d = _to_date(r.get("created_at"))
        if d and start <= d <= end:
            counts[d.isoformat()] += 1

    # Build grid: list of weeks, each week 7 days Sun-Sat style (GitHub uses Sun first)
    weeks: List[List[Dict[str, Any]]] = []
    cursor = start
    # align to Sunday
    while cursor.weekday() != 6:
        cursor -= timedelta(days=1)
    while cursor <= end:
        week = []
        for _ in range(7):
            if cursor > end:
                break
            key = cursor.isoformat()
            c = counts.get(key, 0)
            week.append({"date": key, "count": c, "level": _activity_level(c)})
            cursor += timedelta(days=1)
        if week:
            weeks.append(week)

    return {
        "weeks": weeks,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "total_active_days": sum(1 for c in counts.values() if c > 0),
    }


def _activity_level(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 1:
        return 1
    if count <= 3:
        return 2
    if count <= 5:
        return 3
    return 4


def compute_streaks(quiz_results: List[Dict]) -> Dict[str, int]:
    dates = sorted(
        {
            _to_date(q.get("created_at") or q.get("attempt_date"))
            for q in quiz_results
            if q.get("score") is not None and _to_date(q.get("created_at") or q.get("attempt_date"))
        }
    )
    if not dates:
        return {"current_streak": 0, "longest_streak": 0}

    longest = current = 1
    run = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            run += 1
        else:
            longest = max(longest, run)
            run = 1
    longest = max(longest, run)

    # current streak from today backward
    today = date.today()
    day_set = set(dates)
    cur = 0
    d = today
    while d in day_set:
        cur += 1
        d -= timedelta(days=1)
    if today not in day_set and (today - timedelta(days=1)) in day_set:
        d = today - timedelta(days=1)
        cur = 0
        while d in day_set:
            cur += 1
            d -= timedelta(days=1)

    return {"current_streak": cur, "longest_streak": longest}


def topic_performance(quiz_results: List[Dict]) -> List[Dict[str, Any]]:
    by_topic: Dict[str, List[float]] = defaultdict(list)
    for q in quiz_results:
        if q.get("score") is None:
            continue
        try:
            by_topic[q.get("topic") or "general"].append(float(q["score"]))
        except (TypeError, ValueError):
            continue
    out = []
    for topic, scores in sorted(by_topic.items()):
        avg = round(sum(scores) / len(scores), 1)
        out.append({"topic": topic, "avg_score": avg, "attempts": len(scores)})
    out.sort(key=lambda x: x["avg_score"], reverse=True)
    return out


def difficulty_breakdown(quiz_results: List[Dict]) -> Dict[str, float]:
    buckets = {"easy": [], "medium": [], "hard": []}
    for q in quiz_results:
        if q.get("score") is None:
            continue
        diff = (q.get("difficulty") or "medium").lower()
        if diff not in buckets:
            diff = "medium"
        try:
            buckets[diff].append(float(q["score"]))
        except (TypeError, ValueError):
            continue
    return {
        k: round(sum(v) / len(v), 1) if v else 0
        for k, v in buckets.items()
    }


def quiz_summary_stats(quiz_results: List[Dict]) -> Dict[str, Any]:
    completed = [q for q in quiz_results if q.get("score") is not None]
    scores = []
    correct = 0
    total_q = 0
    for q in completed:
        try:
            scores.append(float(q["score"]))
        except (TypeError, ValueError):
            continue
        total_q += int(q.get("total_questions") or 0)
        correct += int(q.get("correct_answers") or 0)

    topics = topic_performance(quiz_results)
    strongest = topics[0]["topic"] if topics else "—"
    weakest = topics[-1]["topic"] if len(topics) > 1 else (topics[0]["topic"] if topics else "—")

    accuracy = round((correct / total_q) * 100, 1) if total_q else (round(sum(scores) / len(scores), 1) if scores else 0)

    return {
        "accuracy_pct": accuracy,
        "questions_attempted": total_q or len(completed) * 5,
        "correct_answers": correct,
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "quizzes_solved": len(completed),
        "strongest_topic": strongest,
        "weakest_topic": weakest,
        "topic_breakdown": topics,
        "difficulty_breakdown": difficulty_breakdown(quiz_results),
    }

def build_dashboard_metrics(quiz_results, weak_topics):
    completed = [r for r in quiz_results if _safe_score(r) is not None]
    attempts = len(completed)
    avg_score = round(
        sum(_safe_score(r) for r in completed) / attempts, 2
    ) if attempts else 0
    skill_growth = min(100, int(avg_score + attempts * 1.5))
    consistency = min(100, int(attempts * 5))

    return {
        "attempts": attempts,
        "average_score": avg_score,
        "weak_topics_count": len(weak_topics),
        "skill_growth": skill_growth,
        "consistency": consistency,
        "study_time_minutes": sum(int(r.get("time_spent_seconds") or 0) for r in completed) // 60,
    }


def _safe_score(item) -> float | None:
    raw = item.get("score")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None

def _safe_score(item) -> float | None:
    """Return score as float, or None if quiz attempt is incomplete."""
    raw = item.get("score")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def detect_weak_subjects(quiz_results):
    """
    Detect weak subjects/topics from quiz history.

    Signals used:
    - avg_score below 40%
    - recent_low_rate (how often the last N attempts are below 40%)
    - high_time_spent with low performance (struggles without improvement)
    - score variance (unstable learning sometimes indicates conceptual gaps)
    """
    if not quiz_results:
        return []

    topic_stats = {}
    for item in quiz_results:
        score = _safe_score(item)
        if score is None:
            continue
        topic = item.get("topic", "general") or "general"
        time_s = float(item.get("time_spent_seconds") or 0)
        stats = topic_stats.setdefault(
            topic, {"scores": [], "time_spent": [], "recent_scores": []}
        )
        stats["scores"].append(score)
        stats["time_spent"].append(time_s)
        # keep a small rolling window of recent values (last 3)
        stats["recent_scores"] = (stats["recent_scores"] + [score])[-3:]

    weak = []
    for topic, stats in topic_stats.items():
        scores = stats["scores"]
        recent_scores = stats["recent_scores"]
        time_spent = stats["time_spent"]

        avg_score = sum(scores) / max(len(scores), 1)
        avg_time = sum(time_spent) / max(len(time_spent), 1)

        # recent performance: percentage of recent attempts that are below 40%
        recent_low_rate = (
            sum(1 for s in recent_scores if s < 40) / max(len(recent_scores), 1)
        )

        # score variance (simple stability proxy)
        mean = avg_score
        variance = sum((s - mean) ** 2 for s in scores) / max(len(scores), 1)

        reasons = []
        if avg_score < 40:
            reasons.append("Low average performance (<40%)")
        if recent_low_rate >= 0.66 and len(scores) >= 2:
            reasons.append("Recent attempts frequently below 40%")
        if avg_time >= 600 and avg_score < 60:
            # 10 min/question-ish average heuristic; adjust later with real schema
            reasons.append("High time spent without strong improvement")
        if variance >= 4000 and avg_score < 70:
            reasons.append("High inconsistency in scores")

        if avg_score < 40 or (recent_low_rate >= 0.66 and avg_score < 60):
            weak.append(
                {
                    "topic": topic,
                    "avg_score": round(avg_score, 2),
                    "attempts": len(scores),
                    "avg_time_spent_seconds": round(avg_time, 2),
                    "recent_low_rate": round(recent_low_rate, 2),
                    "score_variance": round(variance, 2),
                    "status": "weak",
                    "reasons": reasons[:3],
                }
            )

    return sorted(weak, key=lambda x: (x["avg_score"], -x["recent_low_rate"]))

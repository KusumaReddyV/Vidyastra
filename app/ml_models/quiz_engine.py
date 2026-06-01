from datetime import datetime
import logging
import random

from app.services.data_loader import load_question_bank

logger = logging.getLogger(__name__)

# Legacy fallback if data/question_bank.json is missing
QUESTION_BANK = {}


def _normalize_topic(topic: str) -> str:
    t = (topic or "python").lower().strip()
    aliases = {
        "data structures": "dsa",
        "algorithms": "dsa",
        "database": "dbms",
        "databases": "dbms",
        "operating system": "os",
        "computer networks": "cn",
        "networking": "cn",
        "apt": "aptitude",
    }
    return aliases.get(t, t)


def _normalize_questions(raw_questions, *, topic: str, difficulty: str):
    normalized = []
    for i, q in enumerate(raw_questions or []):
        if not isinstance(q, dict):
            continue
        item = dict(q)
        item.setdefault("id", f"{topic}-{difficulty}-{i}")
        item.setdefault("type", "mcq")
        item.setdefault("options", [])
        item.setdefault("explanation", "")
        normalized.append(item)
    return normalized


def _questions_from_bank(*, topic: str, level: str, count: int = 5):
    bank = load_question_bank()
    topic_key = _normalize_topic(topic)
    level = (level or "easy").lower()
    if level not in ("easy", "medium", "hard"):
        level = "easy"

    pool = list((bank.get(topic_key) or {}).get(level, []))
    if not pool:
        for fallback_topic in bank:
            pool = list((bank.get(fallback_topic) or {}).get(level, []))
            if pool:
                topic_key = fallback_topic
                break

    if not pool:
        pool = [{"id": "gen-1", "type": "mcq", "question": "What is the time complexity of binary search?", "options": ["O(n)", "O(log n)", "O(n^2)", "O(1)"], "answer": "O(log n)", "explanation": "Binary search halves the search space each step."}]

    count = min(count, len(pool))
    selected = random.sample(pool, count) if len(pool) >= count else random.choices(pool, k=count)
    questions = _normalize_questions(selected, topic=topic_key, difficulty=level)

    logger.info("Quiz generated: topic=%s level=%s count=%s", topic_key, level, len(questions))
    return questions


def _adaptive_difficulty(quiz_results, default: str = "easy") -> str:
    """Pick difficulty from recent completed quiz scores."""
    from app.utils import completed_quizzes, quiz_score

    completed = completed_quizzes(quiz_results or [])
    if not completed:
        return default
    recent = completed[-3:]
    scores = [quiz_score(q) for q in recent if quiz_score(q) is not None]
    if not scores:
        return default
    avg = sum(scores) / len(scores)
    if avg >= 85:
        return "hard"
    if avg >= 70:
        return "medium"
    return "easy"


def generate_adaptive_quiz(user_id, topic, difficulty=None, quiz_results=None):
    level = (difficulty or "").lower()
    if level not in ("easy", "medium", "hard"):
        level = _adaptive_difficulty(quiz_results)

    questions = _questions_from_bank(topic=topic, level=level, count=8)
    return {
        "user_id": user_id,
        "topic": _normalize_topic(topic),
        "difficulty": level,
        "timer_seconds": 300,
        "questions": questions,
        "generated_at": datetime.utcnow().isoformat(),
    }


def evaluate_quiz_submission(payload):
    total = int(payload.get("total_questions", 0))
    correct = int(payload.get("correct_answers", 0))
    score = round((correct / total) * 100, 2) if total else 0
    topic = payload.get("topic", "general")
    next_difficulty = "medium" if score >= 70 else "easy"
    if score >= 85:
        next_difficulty = "hard"

    return {
        "topic": topic,
        "difficulty": payload.get("difficulty"),
        "score": score,
        "total_questions": total,
        "correct_answers": correct,
        "time_spent_seconds": payload.get("time_spent_seconds", 0),
        "next_difficulty": next_difficulty,
    }

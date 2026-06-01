from datetime import datetime
from typing import Dict, List, Optional

from app import extensions


COLLECTIONS = [
    "users",
    "student_profiles",
    "resumes",
    "resume_versions",
    "password_reset_tokens",
    "quiz_results",
    "weak_subjects",
    "study_plans",
    "recommendations",
    "learning_progress",
    "chatbot_history",
    "internships",
    "career_roadmaps",
]


def get_db():
    return extensions.mongo_db


def ensure_collections():
    db = get_db()
    if db is None:
        return

    try:
        existing = set(db.list_collection_names())
        for name in COLLECTIONS:
            if name not in existing:
                db.create_collection(name)
    except Exception:
        return


def upsert_student_profile(user_id: str, payload: Dict):
    db = get_db()
    if db is None:
        return
    payload["updated_at"] = datetime.utcnow()
    db.student_profiles.update_one({"user_id": user_id}, {"$set": payload}, upsert=True)


def get_student_profile(user_id: str) -> Optional[Dict]:
    db = get_db()
    if db is None:
        return None
    return db.student_profiles.find_one({"user_id": user_id})


def save_quiz_session(session: Dict) -> Optional[str]:
    """Save a generated quiz (in progress) with questions."""
    db = get_db()
    if db is None:
        return None
    doc = dict(session)
    doc.setdefault("created_at", datetime.utcnow())
    doc.setdefault("status", "in_progress")
    res = db.quiz_results.insert_one(doc)
    return str(res.inserted_id)


def save_quiz_result(result: Dict) -> Optional[str]:
    """Save or update quiz attempt with score and metadata."""
    db = get_db()
    if db is None:
        return None

    quiz_id = result.pop("quiz_id", None)
    result["attempt_date"] = result.get("attempt_date") or datetime.utcnow()
    result["updated_at"] = datetime.utcnow()

    if quiz_id:
        from bson import ObjectId
        from bson.errors import InvalidId

        try:
            db.quiz_results.update_one(
                {"_id": ObjectId(quiz_id), "user_id": result.get("user_id")},
                {"$set": result},
            )
            return quiz_id
        except (InvalidId, TypeError):
            pass

    result.setdefault("created_at", datetime.utcnow())
    res = db.quiz_results.insert_one(result)
    return str(res.inserted_id)


def get_user_quiz_results(user_id: str) -> List[Dict]:
    db = get_db()
    if db is None:
        return []
    rows = list(db.quiz_results.find({"user_id": user_id}).sort("created_at", -1))
    for row in rows:
        row["id"] = str(row.pop("_id", ""))
    return rows


def upsert_weak_subjects(user_id: str, weak_topics: List[Dict]) -> None:
    """
    Store weak topics into `weak_subjects`.
    Uses (user_id, topic) uniqueness via upsert.
    """
    db = get_db()
    if db is None:
        return
    for item in weak_topics:
        topic = item.get("topic")
        if not topic:
            continue
        payload = dict(item)
        payload["user_id"] = user_id
        payload["updated_at"] = datetime.utcnow()
        db.weak_subjects.update_one(
            {"user_id": user_id, "topic": topic},
            {"$set": payload},
            upsert=True,
        )


def get_user_weak_subjects(user_id: str, *, limit: int = 20) -> List[Dict]:
    db = get_db()
    if db is None:
        return []
    return list(
        db.weak_subjects.find({"user_id": user_id}).sort("avg_score", 1).limit(limit)
    )


def get_latest_resume_analysis(user_id: str) -> Optional[Dict]:
    db = get_db()
    if db is None:
        return None
    return db.resumes.find_one({"user_id": user_id}, sort=[("_id", -1)])


def save_resume_version(user_id: str, payload: Dict) -> Optional[str]:
    """
    Store a full resume analysis snapshot as an immutable versioned record.
    """
    db = get_db()
    if db is None:
        return None

    doc = dict(payload)
    doc["user_id"] = user_id
    doc["created_at"] = datetime.utcnow()
    res = db.resume_versions.insert_one(doc)
    return str(res.inserted_id)


def get_resume_history(user_id: str, *, limit: int = 20) -> List[Dict]:
    db = get_db()
    if db is None:
        return []
    return list(db.resume_versions.find({"user_id": user_id}).sort("created_at", -1).limit(limit))


def create_password_reset_token(*, email: str, token_hash: str, expires_at: datetime) -> bool:
    db = get_db()
    if db is None:
        return False
    db.password_reset_tokens.insert_one(
        {"email": email.lower(), "token_hash": token_hash, "expires_at": expires_at, "used": False, "created_at": datetime.utcnow()}
    )
    return True


def mark_password_reset_token_used(*, email: str, token_hash: str) -> None:
    db = get_db()
    if db is None:
        return
    db.password_reset_tokens.update_one(
        {"email": email.lower(), "token_hash": token_hash},
        {"$set": {"used": True, "used_at": datetime.utcnow()}},
    )


def is_password_reset_token_valid(*, email: str, token_hash: str) -> bool:
    db = get_db()
    if db is None:
        return False
    doc = db.password_reset_tokens.find_one({"email": email.lower(), "token_hash": token_hash})
    if not doc:
        return False
    if doc.get("used"):
        return False
    expires_at = doc.get("expires_at")
    if not expires_at:
        return False
    return expires_at > datetime.utcnow()


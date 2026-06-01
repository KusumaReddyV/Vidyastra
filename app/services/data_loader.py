"""Load structured JSON datasets from /data."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _read_json(name: str, default: Any = None) -> Any:
    path = DATA_DIR / name
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_question_bank() -> Dict[str, Any]:
    bank = _read_json("question_bank.json", {})
    if bank:
        return bank
    from app.ml_models.quiz_engine import QUESTION_BANK

    return QUESTION_BANK


@lru_cache(maxsize=1)
def load_mentor_knowledge() -> List[Dict[str, Any]]:
    return _read_json("mentor_knowledge.json", [])


@lru_cache(maxsize=1)
def load_learning_paths() -> Dict[str, Any]:
    return _read_json("learning_paths.json", {})


@lru_cache(maxsize=1)
def load_career_paths() -> Dict[str, Any]:
    return _read_json("career_paths.json", {})


@lru_cache(maxsize=1)
def load_skill_gap_rules() -> Dict[str, Any]:
    return _read_json("skill_gap_rules.json", {})

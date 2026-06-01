import json
from pathlib import Path


def load_question_bank():
    data_path = Path(__file__).parent / "sample_data" / "question_bank.json"
    if not data_path.exists():
        return {}
    return json.loads(data_path.read_text(encoding="utf-8"))


def load_chatbot_seed_data():
    data_path = Path(__file__).parent / "sample_data" / "chatbot_seed.json"
    if not data_path.exists():
        return []
    return json.loads(data_path.read_text(encoding="utf-8"))

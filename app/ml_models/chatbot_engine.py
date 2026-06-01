"""Mentor responses via rule-based knowledge base."""

from app.services.mentor_service import clear_history, generate_mentor_response


def generate_chatbot_response(user_id: str, question: str) -> str:
    return generate_mentor_response(user_id, question)


def reset_mentor_session() -> None:
    clear_history()

import fitz  # PyMuPDF
import logging

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf'}

def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyMuPDF."""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        return None


def quiz_score(item) -> float | None:
    raw = item.get("score") if isinstance(item, dict) else None
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def completed_quizzes(quiz_results):
    return [r for r in (quiz_results or []) if quiz_score(r) is not None]


def weak_topics_from_quizzes(quiz_results, *, threshold: float = 40.0):
    weak = []
    for r in quiz_results or []:
        score = quiz_score(r)
        if score is not None and score < threshold:
            weak.append(r.get("topic", "general") or "general")
    return sorted(set(weak))

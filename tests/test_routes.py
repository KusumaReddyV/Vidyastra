import json
from unittest.mock import patch

from app.models import User


TEST_USER = User(id="507f1f77bcf86cd799439011", email="test@vidyastra.com", name="Test User")


def _auth_client(client):
    with client.session_transaction() as sess:
        sess["_user_id"] = TEST_USER.id
    return client


@patch.object(User, "get_by_id", return_value=TEST_USER)
def test_index_route(_mock_user, client):
    """Test that the index route returns Vidyastra landing page."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"AI-Powered Learning & Career Growth" in response.data or b"Vidyastra" in response.data


@patch.object(User, "get_by_id", return_value=TEST_USER)
def test_api_analyze_text_success(_mock_user, client):
    """Test that the text re-analysis API endpoint processes valid inputs correctly."""
    client = _auth_client(client)
    payload = {
        "resume_text": "I am a skilled developer with experience in Python and Flask.",
        "job_description": "We seek a Python backend engineer with Flask experience.",
    }
    response = client.post(
        "/api/analyze-text",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "overall_score" in data
    assert "matched_keywords" in data
    assert "python" in data["matched_keywords"]


@patch.object(User, "get_by_id", return_value=TEST_USER)
def test_api_analyze_text_missing_params(_mock_user, client):
    """Test validation errors for the text re-analysis endpoint."""
    client = _auth_client(client)

    response = client.post(
        "/api/analyze-text",
        data=json.dumps({"resume_text": "Only resume text"}),
        content_type="application/json",
    )
    assert response.status_code == 400

    response = client.post(
        "/api/analyze-text",
        data=json.dumps({"job_description": "Only job description"}),
        content_type="application/json",
    )
    assert response.status_code == 400

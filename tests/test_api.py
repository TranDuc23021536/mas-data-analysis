from fastapi.testclient import TestClient
from api.main import app
from app.core.config import settings

client = TestClient(app)
_VALID_HEADERS = {"X-API-Key": settings.API_KEY}


def test_health_no_auth_needed():
    response = client.get("/health")
    assert response.status_code == 200


def test_analyze_rejects_without_api_key():
    response = client.post("/analyze", json={"question": "test"})
    assert response.status_code == 401


def test_analyze_rejects_wrong_api_key():
    response = client.post(
        "/analyze",
        json={"question": "test"},
        headers={"X-API-Key": "wrong_key"},
    )
    assert response.status_code == 401


def test_analyze_empty_question_rejected():
    response = client.post(
        "/analyze",
        json={"question": "   "},
        headers=_VALID_HEADERS,
    )
    assert response.status_code == 400
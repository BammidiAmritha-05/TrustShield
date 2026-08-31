from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_app_metadata():
    """Verify application metadata configuration."""
    assert app.title == "TrustShield AI Backend"
    assert app.version == "0.1.0"
    assert app.description == "Human-centric AI safety copilot backend service"


def test_health_endpoint():
    """Verify GET /health returns 200 OK and expected JSON schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "trustshield-backend"
    assert data["version"] == "0.1.0"
    assert data["phase"] == 1
    assert "ai_readiness" in data
    assert "transcription" in data["ai_readiness"]

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage.session_store import session_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_session_store():
    """Reset in-memory store before each test run."""
    session_store.clear()
    yield
    session_store.clear()


def test_health_regression():
    """Verify GET /health continues working as in Phase 1."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "trustshield-backend"
    assert data["version"] == "0.1.0"
    assert data["phase"] == 1


def test_create_voice_session():
    """Verify voice session creation."""
    payload = {"interaction_type": "voice", "consent": True}
    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["interaction_type"] == "voice"
    assert data["consent"] is True
    assert data["status"] == "created"
    assert "created_at" in data
    assert data["ended_at"] is None


def test_create_text_session():
    """Verify text session creation."""
    payload = {"interaction_type": "text", "consent": True}
    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["interaction_type"] == "text"
    assert data["consent"] is True
    assert data["status"] == "created"


def test_create_demo_session():
    """Verify demo session creation."""
    payload = {"interaction_type": "demo", "consent": True}
    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["interaction_type"] == "demo"
    assert data["consent"] is True
    assert data["status"] == "created"


def test_create_session_consent_required():
    """Verify consent=False is rejected with HTTP 422."""
    payload = {"interaction_type": "voice", "consent": False}
    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 422


def test_create_session_missing_consent():
    """Verify missing consent field is rejected with HTTP 422."""
    payload = {"interaction_type": "voice"}
    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 422


def test_create_session_invalid_interaction_type():
    """Verify unsupported interaction type is rejected with HTTP 422."""
    payload = {"interaction_type": "video", "consent": True}
    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 422


def test_get_session_success():
    """Verify successful session retrieval by ID."""
    create_resp = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    session_id = create_resp.json()["session_id"]

    get_resp = client.get(f"/api/v1/sessions/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["session_id"] == session_id


def test_get_session_not_found():
    """Verify non-existent session ID returns HTTP 404."""
    response = client.get("/api/v1/sessions/non-existent-uuid-1234")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_end_session_success():
    """Verify ending an active session."""
    create_resp = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    session_id = create_resp.json()["session_id"]

    end_resp = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_resp.status_code == 200
    data = end_resp.json()
    assert data["status"] == "ended"
    assert data["ended_at"] is not None


def test_end_already_ended_session():
    """Verify re-ending an already ended session returns client error HTTP 400."""
    create_resp = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    session_id = create_resp.json()["session_id"]

    # First end call -> success
    client.post(f"/api/v1/sessions/{session_id}/end")

    # Second end call -> 400 Bad Request
    re_end_resp = client.post(f"/api/v1/sessions/{session_id}/end")
    assert re_end_resp.status_code == 400
    assert "already ended" in re_end_resp.json()["detail"].lower()


def test_list_session_history():
    """Verify session history returns sessions in newest-first order."""
    client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    client.post("/api/v1/sessions", json={"interaction_type": "text", "consent": True})
    client.post("/api/v1/sessions", json={"interaction_type": "demo", "consent": True})

    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 3
    # Check interaction types in reverse creation order
    assert history[0]["interaction_type"] == "demo"
    assert history[1]["interaction_type"] == "text"
    assert history[2]["interaction_type"] == "voice"

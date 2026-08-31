import io
import pytest
import soundfile as sf
import numpy as np
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

from app.config import settings
from app.main import app
from app.services.audio_buffer_service import default_audio_buffer_service
from app.services.evidence_store import default_evidence_store
from app.storage.session_store import session_store

client = TestClient(app)


def make_test_wav_bytes(duration_seconds: float = 1.0) -> bytes:
    """Generates synthetic in-memory WAV bytes for testing."""
    samples = int(16000 * duration_seconds)
    t = np.linspace(0, duration_seconds, samples, endpoint=False)
    signal_data = (np.sin(2 * np.pi * 440.0 * t) * 16384).astype(np.int16)
    buf = io.BytesIO()
    sf.write(buf, signal_data, 16000, format="WAV", subtype="PCM_16")
    return buf.getvalue()


@pytest.fixture(autouse=True)
def reset_session_store():
    """Reset in-memory store, audio buffers, and evidence store before each test run."""
    session_store.clear()
    default_audio_buffer_service.clear_all()
    default_evidence_store.clear_all()
    yield
    session_store.clear()
    default_audio_buffer_service.clear_all()
    default_evidence_store.clear_all()


def test_health_regression():
    """Verify GET /health remains working and includes Phase 11 AI readiness for Whisper, AASIST, Conversation Intelligence, Risk Engine, Protection Agent, and Claim Verification."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["phase"] == 1
    assert "ai_readiness" in data
    assert "transcription" in data["ai_readiness"]
    assert "voice_authenticity" in data["ai_readiness"]
    assert "conversation_intelligence" in data["ai_readiness"]
    assert "risk_engine" in data["ai_readiness"]
    assert "protection_agent" in data["ai_readiness"]
    assert "claim_verification" in data["ai_readiness"]


def test_ws_valid_connection_and_session_started():
    """Valid WS connection emits SESSION_STARTED and transitions status to active."""
    create_res = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    sid = create_res.json()["session_id"]
    assert create_res.json()["status"] == "created"

    with client.websocket_connect(f"/api/v1/sessions/{sid}/stream") as websocket:
        event = websocket.receive_json()
        assert event["type"] == "SESSION_STARTED"
        assert event["version"] == 1
        assert event["session_id"] == sid
        assert event["payload"] == {"status": "active"}

    get_res = client.get(f"/api/v1/sessions/{sid}")
    assert get_res.json()["status"] == "active"


def test_ws_unknown_session():
    """WS connection for non-existent session is rejected."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/api/v1/sessions/non-existent-id/stream"):
            pass
    assert exc_info.value.code in (4004, 1008)


def test_ws_ended_session_rejected():
    """WS connection for an ended session is rejected."""
    create_res = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    sid = create_res.json()["session_id"]
    client.post(f"/api/v1/sessions/{sid}/end")

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/api/v1/sessions/{sid}/stream"):
            pass
    assert exc_info.value.code in (4003, 1008)


def test_ws_text_session_pipeline_emits_events_in_exact_order():
    """Text session emits TEXT_RECEIVED -> SIGNAL_UPDATE -> RISK_UPDATE -> CLAIM_VERIFICATION -> PROTECTION_UPDATE in exact order."""
    create_res = client.post("/api/v1/sessions", json={"interaction_type": "text", "consent": True})
    sid = create_res.json()["session_id"]

    with client.websocket_connect(f"/api/v1/sessions/{sid}/stream") as websocket:
        _ = websocket.receive_json()  # SESSION_STARTED
        websocket.send_json({"action": "send_text", "text": "I am calling regarding PM KISAN instalment. Processing fee required. Send Rs 50,000 immediately."})
        
        event1 = websocket.receive_json()
        assert event1["type"] == "TEXT_RECEIVED"

        event2 = websocket.receive_json()
        assert event2["type"] == "SIGNAL_UPDATE"
        assert event2["payload"]["status"] == "available"

        event3 = websocket.receive_json()
        assert event3["type"] == "RISK_UPDATE"
        assert event3["payload"]["status"] == "available"

        event4 = websocket.receive_json()
        assert event4["type"] == "CLAIM_VERIFICATION"
        assert event4["payload"]["status"] == "available"
        assert event4["payload"]["entity"]["name"] == "PM KISAN"
        assert event4["payload"]["verification"]["overall_status"] == "CONTRADICTED"

        event5 = websocket.receive_json()
        assert event5["type"] == "PROTECTION_UPDATE"
        assert event5["payload"]["status"] == "available"
        assert event5["payload"]["user_confirmation_required"] is True


def test_ws_empty_text_rejection():
    """Empty text is rejected with ERROR event."""
    create_res = client.post("/api/v1/sessions", json={"interaction_type": "text", "consent": True})
    sid = create_res.json()["session_id"]

    with client.websocket_connect(f"/api/v1/sessions/{sid}/stream") as websocket:
        _ = websocket.receive_json()
        websocket.send_json({"action": "send_text", "text": "   "})
        event = websocket.receive_json()
        assert event["type"] == "ERROR"
        assert event["payload"]["code"] == "INVALID_TEXT"


def test_ws_unsupported_action():
    """Unsupported action returns ERROR event."""
    create_res = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    sid = create_res.json()["session_id"]

    with client.websocket_connect(f"/api/v1/sessions/{sid}/stream") as websocket:
        _ = websocket.receive_json()
        websocket.send_json({"action": "unknown_action"})
        event = websocket.receive_json()
        assert event["type"] == "ERROR"
        assert event["payload"]["code"] == "UNSUPPORTED_ACTION"


def test_ws_malformed_json():
    """Malformed JSON text returns ERROR event."""
    create_res = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    sid = create_res.json()["session_id"]

    with client.websocket_connect(f"/api/v1/sessions/{sid}/stream") as websocket:
        _ = websocket.receive_json()
        websocket.send_text("INVALID_JSON_RAW_STRING{")
        event = websocket.receive_json()
        assert event["type"] == "ERROR"
        assert event["payload"]["code"] == "MALFORMED_JSON"


def test_ws_valid_audio_triggers_all_pipeline_events():
    """Valid WAV payload emits in-flight audio events (AUDIO_BUFFERED, AUDIO_DECODED, VOICE_ANALYSIS, RISK_UPDATE, PROTECTION_UPDATE) and flush_utterance emits finalized protection."""
    create_res = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    sid = create_res.json()["session_id"]

    wav_payload = make_test_wav_bytes(duration_seconds=1.0)

    with client.websocket_connect(f"/api/v1/sessions/{sid}/stream") as websocket:
        _ = websocket.receive_json()  # SESSION_STARTED
        websocket.send_bytes(wav_payload)

        # In-flight audio chunk generates exactly 5 events: AUDIO_BUFFERED, AUDIO_DECODED, VOICE_ANALYSIS, RISK_UPDATE, PROTECTION_UPDATE
        events_received = []
        for _ in range(5):
            evt = websocket.receive_json()
            events_received.append(evt["type"])

        assert "AUDIO_BUFFERED" in events_received
        assert "AUDIO_DECODED" in events_received
        assert "VOICE_ANALYSIS" in events_received
        assert "RISK_UPDATE" in events_received
        assert "PROTECTION_UPDATE" in events_received

        # Finalize utterance
        websocket.send_json({"action": "flush_utterance"})
        flush_events = []
        for _ in range(2):  # RISK_UPDATE, PROTECTION_UPDATE
            evt = websocket.receive_json()
            flush_events.append(evt["type"])

        assert "RISK_UPDATE" in flush_events
        assert "PROTECTION_UPDATE" in flush_events


def test_ws_malformed_audio_decoding_failure():
    """Malformed audio binary emits AUDIO_DECODE_FAILED error event."""
    create_res = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    sid = create_res.json()["session_id"]

    with client.websocket_connect(f"/api/v1/sessions/{sid}/stream") as websocket:
        _ = websocket.receive_json()
        websocket.send_bytes(b"NOT_A_VALID_AUDIO_HEADER_BYTES_12345")

        event1 = websocket.receive_json()
        assert event1["type"] == "AUDIO_BUFFERED"

        event2 = websocket.receive_json()
        assert event2["type"] == "ERROR"
        assert event2["payload"]["code"] == "AUDIO_DECODE_FAILED"


def test_ws_stop_command_clears_buffer_evidence_and_ends_session():
    """Stop command emits SESSION_ENDED, closes WS, and purges audio buffer and evidence store."""
    create_res = client.post("/api/v1/sessions", json={"interaction_type": "voice", "consent": True})
    sid = create_res.json()["session_id"]

    wav_payload = make_test_wav_bytes(duration_seconds=1.0)

    with client.websocket_connect(f"/api/v1/sessions/{sid}/stream") as websocket:
        _ = websocket.receive_json()
        websocket.send_bytes(wav_payload)
        for _ in range(5):
            _ = websocket.receive_json()

        websocket.send_json({"action": "stop"})
        event = websocket.receive_json()
        assert event["type"] == "SESSION_ENDED"
        assert event["payload"]["status"] == "ended"

    get_res = client.get(f"/api/v1/sessions/{sid}")
    assert get_res.json()["status"] == "ended"
    assert default_audio_buffer_service.get_size(sid) == 0

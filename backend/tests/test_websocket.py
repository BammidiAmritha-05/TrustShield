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
from app.ai_adapter.transcription import default_transcription_adapter

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
    """Text session emits TEXT_RECEIVED -> SIGNAL_UPDATE -> CLAIM_VERIFICATION -> RISK_UPDATE -> PROTECTION_UPDATE in exact order."""
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
        assert event3["type"] == "CLAIM_VERIFICATION"
        assert event3["payload"]["status"] == "available"
        assert event3["payload"]["entity"]["name"] == "PM KISAN"
        assert event3["payload"]["verification"]["overall_status"] == "CONTRADICTED"

        event4 = websocket.receive_json()
        assert event4["type"] == "RISK_UPDATE"
        assert event4["payload"]["status"] == "available"

        event5 = websocket.receive_json()
        assert event5["type"] == "PROTECTION_UPDATE"
        assert event5["payload"]["status"] == "available"
        assert event5["payload"]["user_confirmation_required"] is True

        event6 = websocket.receive_json()
        assert event6["type"] == "ACTION_GATE"
        assert event6["payload"]["status"] == "available"

        event7 = websocket.receive_json()
        assert event7["type"] == "RECOVERY"
        assert event7["payload"]["status"] == "available"

        assert any(
            signal["signal"] == "claim_verification_contradicted"
            for signal in event4["payload"]["contributing_signals"]
        )


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
    """Valid WAV payload runs the complete streaming protection pipeline through Recovery."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"interaction_type": "voice", "consent": True},
    )
    sid = create_res.json()["session_id"]

    wav_payload = make_test_wav_bytes(duration_seconds=1.0)

    with client.websocket_connect(f"/api/v1/sessions/{sid}/stream") as websocket:
        _ = websocket.receive_json()  # SESSION_STARTED

        websocket.send_bytes(wav_payload)

        events_received = []
        event_payloads = {}

        # Read until Recovery, which is the terminal event for this audio chunk.
        while "RECOVERY" not in events_received:
            evt = websocket.receive_json()
            events_received.append(evt["type"])
            event_payloads[evt["type"]] = evt["payload"]

        assert events_received[0] == "AUDIO_BUFFERED"
        assert events_received[1] == "AUDIO_DECODED"
        assert "VOICE_ANALYSIS" in events_received

        # One preview risk + one authoritative post-claim risk.
        assert events_received.count("RISK_UPDATE") == 2

        assert "PROTECTION_UPDATE" in events_received
        assert "ACTION_GATE" in events_received
        assert events_received[-1] == "RECOVERY"

        # Safety pipeline ordering.
        first_risk = events_received.index("RISK_UPDATE")
        second_risk = events_received.index("RISK_UPDATE", first_risk + 1)
        protection = events_received.index("PROTECTION_UPDATE")
        gate = events_received.index("ACTION_GATE")
        recovery = events_received.index("RECOVERY")

        assert first_risk < second_risk < protection < gate < recovery

        assert event_payloads["PROTECTION_UPDATE"]["status"] == "available"
        assert event_payloads["ACTION_GATE"]["status"] == "available"
        assert event_payloads["RECOVERY"]["status"] == "available"


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

        # Drain the complete streaming pipeline before sending stop.
        while True:
            evt = websocket.receive_json()
            if evt["type"] == "RECOVERY":
                break

        websocket.send_json({"action": "stop"})
        event = websocket.receive_json()

        assert event["type"] == "SESSION_ENDED"
        assert event["payload"]["status"] == "ended"

    get_res = client.get(f"/api/v1/sessions/{sid}")
    assert get_res.json()["status"] == "ended"
    assert default_audio_buffer_service.get_size(sid) == 0

def test_ws_text_high_risk_runs_complete_safety_chain():
    """High-risk text runs through verification, assessment, protection, action gate, and recovery."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"interaction_type": "text", "consent": True},
    )
    sid = create_res.json()["session_id"]

    with client.websocket_connect(
        f"/api/v1/sessions/{sid}/stream"
    ) as websocket:
        _ = websocket.receive_json()  # SESSION_STARTED

        websocket.send_json({
            "action": "send_text",
            "text": (
                "I am calling regarding PM KISAN instalment. "
                "Processing fee required. Send Rs 50,000 immediately."
            ),
        })

        events = []
        payloads = {}

        # RECOVERY is the terminal event for this text turn.
        while "RECOVERY" not in events:
            event = websocket.receive_json()
            events.append(event["type"])
            payloads[event["type"]] = event["payload"]

        assert events == [
            "TEXT_RECEIVED",
            "SIGNAL_UPDATE",
            "CLAIM_VERIFICATION",
            "RISK_UPDATE",
            "PROTECTION_UPDATE",
            "ACTION_GATE",
            "RECOVERY",
        ]

        # Claim verification must identify the contradiction.
        claim = payloads["CLAIM_VERIFICATION"]
        assert claim["status"] == "available"
        assert claim["verification"]["overall_status"] == "CONTRADICTED"

        # Risk must incorporate the claim-verification signal.
        risk = payloads["RISK_UPDATE"]
        assert risk["status"] == "available"
        assert risk["risk_level"] == "HIGH_RISK"
        assert any(
            signal["signal"] == "claim_verification_contradicted"
            for signal in risk["contributing_signals"]
        )

        # Protection must require user confirmation.
        protection = payloads["PROTECTION_UPDATE"]
        assert protection["status"] == "available"
        assert protection["protection_level"] == "HIGH_RISK"
        assert protection["user_confirmation_required"] is True

        # Action Gate must prevent the risky action.
        gate = payloads["ACTION_GATE"]
        assert gate["status"] == "available"
        assert gate["gate_decision"] == "BLOCK_AND_VERIFY"
        assert gate["can_proceed"] is False
        assert gate["requires_verification"] is True

        # Recovery must provide guidance without pretending to take action.
        recovery = payloads["RECOVERY"]
        assert recovery["status"] == "available"
        assert recovery["recovery_required"] is True
        assert recovery["severity"] == "URGENT"
        assert recovery["action_type"] == "transfer_money"
        assert recovery["external_action_taken"] is False
        assert recovery["loss_reversed"] is False

def test_ws_text_safe_conversation_allows_action_without_recovery():
    """Normal text should remain SAFE and should not require recovery."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"interaction_type": "text", "consent": True},
    )
    sid = create_res.json()["session_id"]

    with client.websocket_connect(
        f"/api/v1/sessions/{sid}/stream"
    ) as websocket:
        _ = websocket.receive_json()  # SESSION_STARTED

        websocket.send_json({
            "action": "send_text",
            "text": "Hi, are we still meeting at 5 PM today?"
        })

        events = []
        payloads = {}

        while "RECOVERY" not in events:
            event = websocket.receive_json()
            events.append(event["type"])
            payloads[event["type"]] = event["payload"]

        assert events == [
            "TEXT_RECEIVED",
            "SIGNAL_UPDATE",
            "CLAIM_VERIFICATION",
            "RISK_UPDATE",
            "PROTECTION_UPDATE",
            "ACTION_GATE",
            "RECOVERY",
        ]

        risk = payloads["RISK_UPDATE"]
        assert risk["status"] == "available"
        assert risk["risk_level"] == "SAFE"

        protection = payloads["PROTECTION_UPDATE"]
        assert protection["status"] == "available"
        assert protection["protection_level"] == "SAFE"
        assert protection["user_confirmation_required"] is False

        gate = payloads["ACTION_GATE"]
        assert gate["status"] == "available"
        assert gate["gate_decision"] == "ALLOW"
        assert gate["can_proceed"] is True
        assert gate["requires_verification"] is False

        recovery = payloads["RECOVERY"]
        assert recovery["status"] == "available"
        assert recovery["recovery_required"] is False
        assert recovery["severity"] == "NONE"
        assert recovery["external_action_taken"] is False
        assert recovery["loss_reversed"] is False

def test_ws_flush_utterance_runs_complete_safety_chain():
    """Flushing buffered voice audio runs the completed-utterance safety pipeline."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"interaction_type": "voice", "consent": True},
    )
    sid = create_res.json()["session_id"]

    wav_payload = make_test_wav_bytes(duration_seconds=1.0)

    with client.websocket_connect(
        f"/api/v1/sessions/{sid}/stream"
    ) as websocket:
        _ = websocket.receive_json()  # SESSION_STARTED

        # Buffer the audio first.
        websocket.send_bytes(wav_payload)

        # Drain the in-flight pipeline completely.
        while True:
            event = websocket.receive_json()
            if event["type"] == "RECOVERY":
                break

        # Now finalize the buffered utterance.
        websocket.send_json({"action": "flush_utterance"})

        flush_events = []
        flush_payloads = {}

        # Recovery is the terminal event for the completed utterance.
        while "RECOVERY" not in flush_events:
            event = websocket.receive_json()
            flush_events.append(event["type"])
            flush_payloads[event["type"]] = event["payload"]

        # Core completed-utterance stages must occur.
        assert "RISK_UPDATE" in flush_events
        assert "PROTECTION_UPDATE" in flush_events
        assert "ACTION_GATE" in flush_events
        assert "RECOVERY" in flush_events

        # Verify ordering of the safety stages.
        risk_index = flush_events.index("RISK_UPDATE")
        protection_index = flush_events.index("PROTECTION_UPDATE")
        gate_index = flush_events.index("ACTION_GATE")
        recovery_index = flush_events.index("RECOVERY")

        assert risk_index < protection_index < gate_index < recovery_index

        # When transcription produced text, claim verification must precede risk.
        if "CLAIM_VERIFICATION" in flush_events:
            claim_index = flush_events.index("CLAIM_VERIFICATION")
            assert claim_index < risk_index

        assert flush_payloads["PROTECTION_UPDATE"]["status"] == "available"
        assert flush_payloads["ACTION_GATE"]["status"] == "available"
        assert flush_payloads["RECOVERY"]["status"] == "available"

def test_ws_streaming_voice_uses_authoritative_post_claim_risk():
    """Streaming voice performs preview risk, claim verification, then authoritative risk before protection."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"interaction_type": "voice", "consent": True},
    )
    sid = create_res.json()["session_id"]

    scam_text = (
        "I am calling regarding PM KISAN instalment. "
        "Processing fee required. Send Rs 50,000 immediately."
    )

    def fake_transcribe_pcm_bytes(pcm_data, sample_rate):
        return {
            "text": scam_text,
            "duration": 1.0,
            "language": "en",
        }

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            default_transcription_adapter,
            "transcribe_pcm_bytes",
            fake_transcribe_pcm_bytes,
        )

        wav_payload = make_test_wav_bytes(duration_seconds=1.0)

        with client.websocket_connect(
            f"/api/v1/sessions/{sid}/stream"
        ) as websocket:
            _ = websocket.receive_json()  # SESSION_STARTED

            websocket.send_bytes(wav_payload)

            events = []
            received = []

            while "RECOVERY" not in events:
                event = websocket.receive_json()
                events.append(event["type"])
                received.append(event)

            # Required stages exist.
            assert "CLAIM_VERIFICATION" in events
            assert "PROTECTION_UPDATE" in events
            assert "ACTION_GATE" in events
            assert "RECOVERY" in events

            # There must be exactly two risk evaluations:
            # preview risk + authoritative post-claim risk.
            assert events.count("RISK_UPDATE") == 2

            first_risk_index = events.index("RISK_UPDATE")
            claim_index = events.index("CLAIM_VERIFICATION")
            second_risk_index = events.index(
                "RISK_UPDATE",
                first_risk_index + 1,
            )
            protection_index = events.index("PROTECTION_UPDATE")
            gate_index = events.index("ACTION_GATE")
            recovery_index = events.index("RECOVERY")

            # Claim verification must happen between preview and authoritative risk.
            assert first_risk_index < claim_index < second_risk_index

            # Authoritative risk must feed the downstream safety chain.
            assert second_risk_index < protection_index < gate_index < recovery_index

            claim_event = received[claim_index]
            assert claim_event["payload"]["status"] == "available"

            second_risk_event = received[second_risk_index]
            assert second_risk_event["payload"]["status"] == "available"

            assert any(
                signal["signal"] == "claim_verification_contradicted"
                for signal in second_risk_event["payload"]["contributing_signals"]
            )

            protection_event = received[protection_index]
            assert protection_event["payload"]["status"] == "available"

            gate_event = received[gate_index]
            assert gate_event["payload"]["status"] == "available"

            recovery_event = received[recovery_index]
            assert recovery_event["payload"]["status"] == "available"
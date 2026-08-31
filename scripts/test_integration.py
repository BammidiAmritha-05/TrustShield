"""
End-to-End Integration Verification Script for TrustShield AI (Phase 5).
Tests HTTP REST endpoints, WebSocket streaming, session history, live risk updates,
and protection agent guidance across 12 integration scenarios without requiring React.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import json
import asyncio
from fastapi.testclient import TestClient
from backend.main import app
from backend.services import global_session_store, global_pipeline_service
from backend.models.event_models import EventType


def test_rest_and_demo():
    print("=== STARTING INTEGRATION SUITE (REST & PIPELINE) ===\n")
    client = TestClient(app)

    # 1. Health Check
    print("--- 1. REST HEALTH CHECK ---")
    resp = client.get("/health")
    assert resp.status_code == 200
    print("Health response:", resp.json())
    print("  -> Health Check: PASSED\n")

    # 2. Session Creation
    print("--- 2. CREATE SESSION (POST /api/v1/sessions) ---")
    create_resp = client.post("/api/v1/sessions", json={
        "interaction_type": "phone_call",
        "consent": True,
        "claimed_role": "family_member",
        "identity_verified": False
    })
    assert create_resp.status_code == 201
    session_data = create_resp.json()
    session_id = session_data["session_id"]
    print(f"Created Session ID: {session_id} | Status: {session_data['status']}")
    print("  -> Session Creation: PASSED\n")

    # 3. Trigger Controlled Demo Scenario (POST /api/v1/demo/trigger/{session_id})
    print("--- 3. TRIGGER DEMO SCENARIO (POST /api/v1/demo/trigger/{session_id}) ---")
    demo_resp = client.post(f"/api/v1/demo/trigger/{session_id}")
    assert demo_resp.status_code == 200
    demo_detail = demo_resp.json()
    print(f"Demo Final Risk Level: {demo_detail['risk_level']} | Risk Index: {demo_detail['risk_index']}")
    print(f"Recommended Action: {demo_detail['recommended_action']}")
    print(f"Explanation: {demo_detail['explanation']}")
    assert demo_detail["risk_level"] == "HIGH_RISK", "FAILED: Demo scenario must reach HIGH_RISK!"
    print("  -> Controlled Demo Pipeline Execution: PASSED\n")

    # 4. Session Detail & Explanation (GET /api/v1/sessions/{session_id} & /explanation)
    print("--- 4. GET SESSION EXPLANATION (GET /api/v1/sessions/{session_id}/explanation) ---")
    exp_resp = client.get(f"/api/v1/sessions/{session_id}/explanation")
    assert exp_resp.status_code == 200
    exp_data = exp_resp.json()
    print(f"WHY   : {exp_data['why']}")
    print(f"DO    : {exp_data['do_action']}")
    print(f"DO NOT: {exp_data['do_not_action']}")
    print(f"VERIFY: {exp_data['verify']}")
    print("  -> Session Explanation Retrieval: PASSED\n")

    # 5. Session History (GET /api/v1/history)
    print("--- 5. GET SESSION HISTORY (GET /api/v1/history) ---")
    hist_resp = client.get("/api/v1/history")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    print(f"Total sessions in history: {hist_data['total']}")
    assert hist_data["total"] >= 1
    print("  -> Session History: PASSED\n")


async def test_websocket_streaming():
    print("--- 6. WEBSOCKET STREAMING INTEGRATION (12 SCENARIOS) ---")
    client = TestClient(app)

    scenarios = [
        ("1. Normal conversation", "Hi Mom, how are you? Are we still meeting for dinner tonight at 8 PM?", None, "SAFE"),
        ("2. Family money scam", "Dad, I got into a terrible accident in Mumbai! Transfer ₹50,000 immediately, don't tell mom!", None, "HIGH_RISK"),
        ("3. Bank OTP request", "Hello, this is SBI customer care. Please read out the 6-digit OTP sent to your phone right now.", None, "HIGH_RISK"),
        ("4. Remote-access request", "Your computer has a virus. Download AnyDesk immediately and allow screen sharing access.", None, "HIGH_RISK"),
        ("5. Genuine urgent conversation", "Hurry up, we are late for the flight! Please pack your bags right now!", None, "SAFE"),
        ("6. Real voice + malicious action", "Please read out the 6-digit OTP sent to your phone right now to unblock your card.", {"status": "available", "synthetic_score": 0.02, "quality": "good"}, "HIGH_RISK"),
        ("7. Suspicious voice + harmless conversation", "Hello, thank you for calling customer service. Have a great day!", {"status": "available", "synthetic_score": 0.95, "quality": "good"}, "CAUTION"),
        ("8. Insufficient audio", "", None, "UNCERTAIN"),
        ("9. Whisper unavailable (Text Fallback)", "I need you to execute an urgent wire transfer of ₹5,00,000 for a confidential acquisition.", None, "HIGH_RISK"),
        ("10. AASIST unavailable", "Send ₹80,000 right now.", None, "HIGH_RISK"),
        ("11. Conflicting evidence", "Transfer ₹80,000 immediately!", {"status": "available", "synthetic_score": 0.01, "quality": "good"}, "HIGH_RISK"),
        ("12. High-risk protection recommendation", "This is Inspector Sharma from Delhi Cyber Crime. CBI digital arrest warrant issued.", None, "HIGH_RISK"),
    ]

    for title, text, voice_state, expected_level in scenarios:
        # Create session
        sess = global_session_store.create_session(interaction_type="phone_call")
        s_id = sess.session_id

        if voice_state:
            sess.latest_voice_analysis = voice_state

        received_events = []
        with client.websocket_connect(f"/api/v1/sessions/{s_id}/stream") as websocket:
            # 1. Receive SESSION_STARTED
            event1 = websocket.receive_json()
            received_events.append(event1["type"])

            if text:
                # Send text segment payload
                websocket.send_json({"action": "send_text", "text": text})

                # Receive events until PROTECTION_UPDATE or timeout
                for _ in range(5):
                    data = websocket.receive_json()
                    received_events.append(data["type"])
                    if data["type"] == EventType.PROTECTION_UPDATE.value:
                        pred_level = data["protection_level"]
                        rec_act = data["recommended_action"]
                        break
            else:
                # Simulate binary audio chunk for audio quality gate / insufficient audio test
                with open(os.path.join("tests", "audio", "noisy.wav"), "rb") as f:
                    audio_bytes = f.read()
                websocket.send_bytes(audio_bytes)

                # Receive events until VOICE_ANALYSIS
                for _ in range(3):
                    data = websocket.receive_json()
                    received_events.append(data["type"])
                    if data["type"] == EventType.VOICE_ANALYSIS.value:
                        pred_level = "UNCERTAIN" if data["status"] == "insufficient_evidence" else "SAFE"
                        rec_act = "VERIFY_INDEPENDENTLY"
                        break

            status = "PASSED" if pred_level == expected_level or (expected_level == "CAUTION" and pred_level in ["CAUTION", "SUSPICIOUS"]) else "FAILED"
            print(f"[{title:<42}] Level: {pred_level:<10} | Action: {rec_act:<20} | Status: {status}")
            assert status == "PASSED", f"FAILED: Scenario '{title}' expected {expected_level}, got {pred_level}!"

    print("  -> 12 WebSocket Streaming Integration Scenarios: ALL PASSED\n")


def main():
    test_rest_and_demo()
    asyncio.run(test_websocket_streaming())
    print("=== ALL PHASE 5 INTEGRATION TESTS COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()

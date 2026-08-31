# Phase 5: TrustShield AI Integration Layer Documentation

## Overview
Phase 5 connects TrustShield AI's core engines (Whisper ASR, AASIST-L Voice Anti-Spoofing, Conversation Intelligence, Hybrid Evidence Engine, Risk Engine, and Protection Agent) into a unified **FastAPI Backend Service**. The backend exposes REST endpoints and a real-time **WebSocket Streaming Protocol** for consumption by the React frontend.

---

## 1. System Architecture

```
Authorized Audio / Text Chunks
            │
            ▼
   FastAPI WebSocket Router (/api/v1/sessions/{session_id}/stream)
            │
            ▼
    Audio Quality Gate
            │
            ▼
   faster-whisper ASR  ──►  Conversation Intelligence (Phase 2)
            │                           │
            ▼                           ▼
    AASIST-L Voice (Phase 1) ──► Evidence Accumulator (Phase 3)
                                        │
                                        ▼
                                  Temporal Engine
                                        │
                                        ▼
                                   Risk Engine
                                        │
                                        ▼
                                Protection Agent (Phase 4)
                                        │
                                        ▼
                            Versioned WebSocket Events
                                        │
                                        ▼
                                  React Frontend
```

---

## 2. API Endpoints Reference

### REST Endpoints

#### 1. `POST /api/v1/sessions`
Creates a new protection session.
- **Request Payload**:
  ```json
  {
    "interaction_type": "phone_call",
    "consent": true,
    "claimed_role": "family_member",
    "identity_verified": false
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "ts_sess_3d481e68",
    "status": "created",
    "created_at": "2026-08-29T11:45:00Z"
  }
  ```

#### 2. `GET /api/v1/sessions/{session_id}`
Returns details, full transcript, evidence count, and latest risk & protection status.

#### 3. `GET /api/v1/sessions/{session_id}/explanation`
Returns evidence-based decision explanation:
```json
{
  "session_id": "ts_sess_3d481e68",
  "risk_level": "HIGH_RISK",
  "risk_index": 82,
  "confidence": 0.90,
  "explanation": "Safety Policy Triggered (POL_002): Financial transfer or payment link requested under urgency and unverified identity.",
  "why": "Financial transfer requested under high urgency and unverified identity.",
  "do_action": "Pause the transfer immediately and verify the request through an independent channel.",
  "do_not_action": "Do NOT transfer money using payment links, UPI IDs, or bank details provided during this call.",
  "verify": "Contact Anand (Brother) (family_member) via their saved channel: +919876543210."
}
```

#### 4. `GET /api/v1/history`
Returns history of completed/active protection sessions.

#### 5. `POST /api/v1/demo/trigger/{session_id}`
Triggers controlled scam scenario execution through the real AI pipeline for demo purposes.

---

## 3. Real-Time WebSocket Protocol

- **Endpoint**: `WS /api/v1/sessions/{session_id}/stream`
- **Input**:
  - Binary WAV/PCM Audio Chunks.
  - JSON Text payloads: `{"action": "send_text", "text": "..."}` or `{"action": "end_session"}`.
- **Output Events**:
  - `SESSION_STARTED`
  - `TRANSCRIPT_PARTIAL`
  - `TRANSCRIPT_FINAL`
  - `VOICE_ANALYSIS`
  - `SIGNAL_UPDATE`
  - `RISK_UPDATE`
  - `PROTECTION_UPDATE`
  - `ERROR`
  - `SESSION_ENDED`

---

## 4. Privacy & Performance Guarantees

1. **In-Memory Audio Lifecycle**: Audio chunks are buffered temporarily in memory or temporary files solely for windowed analysis, and are **immediately destroyed** post-processing.
2. **Zero Audio Retention**: Raw audio is **never** written to logs or stored permanently on disk.
3. **CPU Optimization**: Pre-warmed model instances at server startup ensure high responsiveness on CPU-only hardware.

---

## 5. Integration Verification
- Ran full integration suite `scripts/test_integration.py`.
- Verified HTTP REST endpoints, WebSocket streaming, session history, and demo trigger across 12 scenarios with 100% pass rate.

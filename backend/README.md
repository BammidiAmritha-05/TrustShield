# TrustShield AI Backend

Standalone FastAPI backend foundation for **TrustShield AI**, a human-centric AI safety copilot that helps users understand suspicious interactions and verify risky claims before taking dangerous actions.

## Current Progress: Phase 11 Complete (Claim Verification & Official Source Verification)

### Setup & Installation

1. **Prerequisites**: Python 3.10+ (tested on Python 3.13.7).
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Environment settings (`app/config.py`):
- `APP_ENV`: Application environment (`development`)
- `HOST`: Bind host (`127.0.0.1`)
- `PORT`: Bind port (`8000`)
- `LOG_LEVEL`: Logging verbosity (`INFO`)
- `TRUSTSHIELD_AI_ROOT`: Path to AI package (`D:\TrustShield\ai`)

### Running the Application

To start the development server:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## API Documentation

### Health Endpoint
- **GET** `/health` -> Returns system status, phase info, and AI readiness (`HTTP 200 OK`).
  ```json
  {
    "status": "ok",
    "service": "trustshield-backend",
    "version": "0.1.0",
    "phase": 1,
    "ai_readiness": {
      "transcription": "READY",
      "voice_authenticity": "READY",
      "conversation_intelligence": "READY",
      "risk_engine": "READY",
      "protection_agent": "READY",
      "claim_verification": "READY"
    }
  }
  ```

### Protection Session API (`/api/v1/sessions`)
- **Create Session**: `POST /api/v1/sessions` (`{"interaction_type": "voice", "consent": true}`)
- **Retrieve Session**: `GET /api/v1/sessions/<session_id>`
- **End Session**: `POST /api/v1/sessions/<session_id>/end`
- **List History**: `GET /api/v1/sessions`

### WebSocket Streaming Endpoint (`/api/v1/sessions/{session_id}/stream`)

Connect over WebSocket:
`ws://127.0.0.1:8000/api/v1/sessions/{session_id}/stream`

#### Event Protocol (Server -> Client)
Events emitted during streaming:
`SESSION_STARTED` $\to$ `AUDIO_BUFFERED` $\to$ `AUDIO_DECODED` $\to$ `TRANSCRIPT_FINAL` $\to$ `VOICE_ANALYSIS` $\to$ `SIGNAL_UPDATE` $\to$ `RISK_UPDATE` $\to$ `CLAIM_VERIFICATION` $\to$ `PROTECTION_UPDATE`

- **Claim Verification Event**:
  ```json
  {
    "type": "CLAIM_VERIFICATION",
    "version": 1,
    "session_id": "<session_id>",
    "timestamp": "2026-08-29T12:00:00.000000Z",
    "payload": {
      "status": "available",
      "entity": {"name": "PM KISAN", "type": "government_scheme", "jurisdiction": "Central", "status": "VERIFIED"},
      "claims": [{"text": "Verification fee required...", "status": "CONTRADICTED", "evidence": "Official policy explicitly forbids..."}],
      "sources": [{"url": "https://pmkisan.gov.in", "tier": "TIER_1", "source_type": "LIVE_OFFICIAL_SOURCE", "freshness": "FRESH"}],
      "verification": {"overall_status": "CONTRADICTED", "confidence": 0.95}
    }
  }
  ```

---

### Running Automated Tests

Run the full test suite:
```bash
python -m pytest tests/
```

### Phase 11 Limitations

- Integrated existing `verify_official_claim`, `claim_extractor`, `source_retriever`, and `claim_comparator`.
- Final backend hardening and observability belong to Phase 12.

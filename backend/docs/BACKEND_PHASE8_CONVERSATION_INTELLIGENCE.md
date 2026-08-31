# TrustShield AI Backend - Phase 8 Existing Conversation Intelligence Integration

## 1. Existing Conversation Intelligence Implementation
The source of truth for conversation intelligence in TrustShield AI is located at:
`D:\TrustShield\ai\intelligence\conversation_intelligence.py`

Key discovery findings:
- **Module**: `ai.intelligence.conversation_intelligence`
- **Main Function**: `analyze_conversation(text: str, session_context: Optional[Dict[str, Any]] = None) -> ConversationAnalysisResult`
- **Sub-detectors Orchestrated**:
  - `ai.intelligence.intent_detector.detect_intent`
  - `ai.intelligence.action_detector.detect_requested_action`
  - `ai.intelligence.manipulation_detector.detect_manipulation`
  - `ai.intelligence.impersonation_detector.detect_impersonation_claim`
  - `ai.intelligence.context_analyzer.analyze_context`
- **Result Schema**: `ConversationAnalysisResult` (defined in `ai.intelligence.schemas`).

## 2. Adapter Architecture
```text
 [ Client / WebSocket ]
           |
           +---------------------------------+---------------------------------+
           | (Voice Session: TRANSCRIPT_FINAL)| (Text Session: send_text)       |
           v                                 v                                 |
 [ WS /api/v1/sessions/{id}/stream ] <-------+                                 |
           |                                                                   |
           v (asyncio.to_thread)                                               |
 [ AIConversationAdapter ]                                                     |
           |                                                                   |
           v                                                                   v
 D:\TrustShield\ai\intelligence\conversation_intelligence                      |
           |                                                                   |
           v                                                                   v
 EVENT: SIGNAL_UPDATE <--------------------------------------------------------+
```

The backend adapter (`app/ai_adapter/conversation.py`) creates a thin wrapper around `analyze_conversation` without duplicating intent, action, manipulation, or impersonation classifiers.

## 3. AI Root Configuration
Configured centrally via `settings.TRUSTSHIELD_AI_ROOT` (default: `D:\TrustShield\ai`).
`app/ai_adapter/__init__.py` dynamically bootstraps `sys.path` so the AI package is importable without hardcoding absolute paths in backend logic.

## 4. Output Contract & Exposed Signals

### Event Protocol (`SIGNAL_UPDATE`)
```json
{
  "type": "SIGNAL_UPDATE",
  "version": 1,
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": "2026-08-29T12:00:00.000000+00:00",
  "payload": {
    "status": "available",
    "intent": {
      "type": "financial_fraud",
      "confidence": 0.88
    },
    "requested_action": {
      "type": "transfer_money",
      "sensitivity": "critical",
      "confidence": 0.96
    },
    "manipulation": {
      "urgency": 0.96,
      "secrecy": 0.0,
      "fear": 0.0,
      "authority_pressure": 0.0,
      "emotional_pressure": 0.0,
      "threat": 0.0,
      "reward": 0.0,
      "isolation": 0.0,
      "intimidation": 0.0,
      "forced_compliance": 0.0
    },
    "impersonation": {
      "claimed_identity": "family_member",
      "possible_impersonation": true,
      "confidence": 0.88
    },
    "context": {
      "identity_verified": false,
      "unusual_request": true,
      "independent_verification_available": false
    },
    "explanation": "The interaction involves a request to transfer money combined with high urgency from a claimed identity of family member (unverified)."
  }
}
```

## 5. Text Sessions & Voice Sessions
- **Text Sessions**: When `send_text` action is received, text is processed through `AIConversationAdapter` and emits `SIGNAL_UPDATE` directly.
- **Voice Sessions**: When `TRANSCRIPT_FINAL` event is produced from decoded audio, the final text snippet is processed through `AIConversationAdapter` and emits `SIGNAL_UPDATE`.

## 6. Health Readiness
`GET /health` reports readiness status for all three AI services:
```json
{
  "status": "ok",
  "service": "trustshield-backend",
  "version": "0.1.0",
  "phase": 1,
  "ai_readiness": {
    "transcription": "READY",
    "voice_authenticity": "READY",
    "conversation_intelligence": "READY"
  }
}
```

## 7. Privacy & Security
- Conversation intelligence produces structured signal outputs over WebSocket.
- No raw conversation text is permanently persisted to disk or databases.

## 8. Current Limitations
- Temporal evidence accumulation, hybrid risk scoring, and protection actions belong to Phase 9.

## 9. Next Phase
- **Phase 9**: Temporal evidence accumulation + hybrid risk engine.

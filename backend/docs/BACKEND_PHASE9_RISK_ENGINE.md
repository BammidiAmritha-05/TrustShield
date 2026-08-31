# TrustShield AI Backend - Phase 9 Temporal Evidence Accumulation & Hybrid Risk Engine Integration

## 1. Architecture Overview
The source of truth for risk assessment, evidence aggregation, and temporal reasoning in TrustShield AI is located at:
- `D:\TrustShield\ai\risk\risk_engine.py` (`RiskEngine`)
- `D:\TrustShield\ai\evidence\evidence_accumulator.py` (`EvidenceAccumulator`)
- `D:\TrustShield\ai\evidence\temporal_engine.py` (`TemporalEngine`)
- `D:\TrustShield\ai\risk\risk_thresholds.py` (`RiskLevel`, scoring weights)
- `D:\TrustShield\ai\risk\confidence.py` (`calculate_confidence`)
- `D:\TrustShield\ai\risk\risk_policy.py` (`evaluate_safety_policies`)

```text
 [ Voice / Text Input ]
           |
           v
 [ WebSocket /api/v1/sessions/{id}/stream ]
           |
           +----------------------+----------------------+
           |                      |                      |
           v                      v                      v
 [ Whisper Transcription ]  [ AASIST Voice ]  [ Conversation Intelligence ]
 (TRANSCRIPT_FINAL)         (VOICE_ANALYSIS)  (SIGNAL_UPDATE)
           |                      |                      |
           +----------------------+----------------------+
                                  |
                                  v (asyncio.to_thread)
                     [ AIRiskAdapter ]
                                  |
                     [ SessionEvidenceStore ]
                     (Bounded history limit: 50)
                                  |
                                  v
                       [ RiskEngine Evaluation ]
                       - Action Weights (transfer_money, share_otp)
                       - Manipulation Weights (urgency, secrecy)
                       - Impersonation Base Weight
                       - Voice Anti-Spoofing Evidence Weighting
                       - Temporal Escalation Engine
                       - Safety Policy Floors
                                  |
                                  v
                         EVENT: RISK_UPDATE
```

The backend adapter (`app/ai_adapter/risk.py`) and evidence store manager (`app/services/evidence_store.py`) maintain session-isolated evidence streams and execute risk evaluations off-thread without modifying AI model source files.

## 2. Mandatory AASIST Score Semantics Invariant
> [!IMPORTANT]
> `synthetic_score` from AASIST-L represents the Softmax probability of synthetic/spoofed voice (`probs[0, 0]`) in range `[0.0, 1.0]`. It is used strictly as a **voice authenticity signal** in multi-modal risk evaluation.
> It is **never** set equal to `risk_score` directly or reinterpreted as scam probability. A genuine synthetic voice without suspicious intent or risky actions does not trigger critical risk.

## 3. Evidence Model & Temporal Accumulation
- **Normalized Evidence**: Ingested signals are converted to `NormalizedEvidence` items (`signal`, `value`, `confidence`, `source`, `reliability`, `turn_index`).
- **Memory Bounding**: `MAX_EVIDENCE_RECORDS_PER_SESSION = 50`. Oldest evidence items are pruned when history exceeds 50 items.
- **Temporal Escalation**: `TemporalEngine` computes temporal weight decay and multi-turn escalation based on recency and cumulative evidence count.

## 4. Scoring Model & Risk Bands

| Risk Level | Score Range | Description |
| :--- | :--- | :--- |
| `UNCERTAIN` | `None` | Insufficient evidence (e.g. short/unusable audio snippet) |
| `LOW_RISK` | `0.0 - 24.9` | Standard interaction with no significant risk signals |
| `MODERATE_RISK` | `25.0 - 54.9` | Single suspicious tactic or unverified identity claim |
| `HIGH_RISK` | `55.0 - 79.9` | High urgency/secrecy combined with risky action or impersonation |
| `CRITICAL_RISK` | `80.0 - 100.0` | High-risk financial/credential request under pressure or safety policy violation |

## 5. Event Protocol (`RISK_UPDATE`)
```json
{
  "type": "RISK_UPDATE",
  "version": 1,
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": "2026-08-29T12:00:00.000000+00:00",
  "payload": {
    "status": "available",
    "risk_level": "HIGH_RISK",
    "risk_index": 82,
    "confidence": 0.91,
    "explanation": "Safety Policy Triggered (POL_002): Financial transfer or payment link requested under urgency and unverified identity.",
    "contributing_signals": [
      {"signal": "requested_action", "value": "transfer_money", "points": 35.0, "source": "ACTION"},
      {"signal": "manipulation_urgency", "value": 0.96, "points": 19.2, "source": "MANIPULATION"},
      {"signal": "unverified_claimed_identity", "value": "family_member", "points": 20.0, "source": "IMPERSONATION"}
    ],
    "evidence_trace": [
      {"signal": "requested_action", "value": "transfer_money", "confidence": 0.9, "source": "ACTION", "turn_index": 1}
    ],
    "safety_policy_violations": [
      {"policy_id": "POL_002", "floor_score": 80.0, "reason": "Financial transfer or payment link requested under urgency and unverified identity."}
    ],
    "temporal_timeline": [
      {"turn_index": 1, "instantaneous_risk": 74.2, "cumulative_risk": 74.2}
    ]
  }
}
```

## 6. Health Readiness
`GET /health` exposes readiness status across all 4 backend AI components:
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
    "risk_engine": "READY"
  }
}
```

## 7. Privacy & Security
- Session evidence is stored strictly in-memory during active sessions.
- All session evidence is purged automatically upon session termination (`stop` command or REST `/end`).
- Zero raw audio or PCM bytes are stored in evidence history.

## 8. Current Limitations
- Protection Agent safe intervention recommendations belong to Phase 10.

## 9. Next Phase
- **Phase 10**: Protection Agent + Safe Intervention Orchestration.

# TrustShield AI Backend - Phase 10 Protection Agent & Safe Intervention Orchestration

## 1. Architecture Overview
The source of truth for safe intervention recommendations in TrustShield AI is located at:
- `D:\TrustShield\ai\verification\protection_agent.py` (`ProtectionAgent`)
- `D:\TrustShield\ai\verification\verification_planner.py` (`VerificationPlanner`)
- `D:\TrustShield\ai\verification\verification_schema.py` (`VerificationPlan`, `ProtectionLevel`)
- `D:\TrustShield\ai\verification\verification_policy.py` (`ACTION_SAFETY_RULES`)
- `D:\TrustShield\ai\verification\safe_action_generator.py` (`generate_guidance_blocks`)

```text
 [ Multi-Modal AI & Risk Engine ]
 (SIGNAL_UPDATE -> RISK_UPDATE)
               |
               v (asyncio.to_thread)
    [ AIProtectionAdapter ]
               |
    [ ProtectionAgent / VerificationPlanner ]
    - Evaluates Risk Assessment & Action Sensitivity
    - Generates WHY, DO, DO NOT, VERIFY blocks
    - Enforces user_confirmation_required: true
    - Zero autonomous execution (advisory guidance only)
               |
               v
    EVENT: PROTECTION_UPDATE
```

The backend adapter (`app/ai_adapter/protection.py`) wraps `ProtectionAgent` and streams structured `PROTECTION_UPDATE` events over WebSocket.

## 2. Mandatory Human Safety Invariant
> [!IMPORTANT]
> - **Recommendation != Execution**: The Protection Agent returns advisory guidance only. It **never** executes actions autonomously (no call termination, no banking transactions, no automated contact notifications, no operating system / browser controls).
> - **User Confirmation**: `user_confirmation_required: true` is explicitly present in all non-SAFE protection updates.

## 3. AASIST Voice Authenticity Safety Semantics
> [!IMPORTANT]
> `synthetic_score` from AASIST-L is described strictly as voice authenticity evidence ("possible synthetic/spoofed voice characteristics").
> It is **never** reinterpreted as a "95% scam probability" or "95% fraud probability".

## 4. Protection Levels & Recommended Actions

| Protection Level | Risk Band | Recommended Action | Default Guidance |
| :--- | :--- | :--- | :--- |
| `SAFE` | `LOW_RISK` / `0 - 24` | `NO_ACTION_REQUIRED` | Continue with normal caution. |
| `CAUTION` | `MODERATE_RISK` / `25 - 54` | `PAUSE_AND_VERIFY` | Pause before acting; verify request through an independent channel. |
| `HIGH_RISK` | `HIGH_RISK` / `55 - 79` | `PAUSE_TRANSFER` / `DO_NOT_SHARE_OTP` | Pause immediately; do not transfer money or share credentials. |
| `STOP_AND_VERIFY` | `CRITICAL_RISK` / `80 - 100` | `STOP_AND_VERIFY` | Stop interaction; do not share OTP/password/bank details; independently contact official organization. |
| `UNCERTAIN` | `UNCERTAIN` | `VERIFY_INDEPENDENTLY` | Not enough evidence. Stay cautious and verify unexpected requests independently. |

## 5. Event Protocol (`PROTECTION_UPDATE`)
```json
{
  "type": "PROTECTION_UPDATE",
  "version": 1,
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": "2026-08-29T12:00:00.000000+00:00",
  "payload": {
    "status": "available",
    "protection_level": "HIGH_RISK",
    "recommended_action": "PAUSE_TRANSFER",
    "verification_method": "Contact your family member directly using your existing saved phone number.",
    "why": "Financial transfer requested under urgency and unverified identity.",
    "do": "Pause the transfer immediately and verify the request through an independent channel.",
    "do_not": "Do NOT transfer money using payment links, UPI IDs, or bank details provided during this call.",
    "verify": "Contact your family member directly using your existing saved phone number.",
    "draft_verification_message": "Hi there, I received a message regarding an urgent request. Please call me back on my saved number when you see this to confirm.",
    "confidence": 0.91,
    "user_confirmation_required": true,
    "evidence_basis": ["transfer_money", "urgency", "impersonation_family_member"]
  }
}
```

## 6. Strict Event Sequence Order
Every turn emits events strictly in sequence:
1. `SIGNAL_UPDATE` (Conversation Intelligence)
2. `RISK_UPDATE` (Hybrid Risk Engine)
3. `PROTECTION_UPDATE` (Protection Agent)

## 7. Health Readiness
`GET /health` exposes readiness status across all 5 backend AI components:
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
    "protection_agent": "READY"
  }
}
```

## 8. Privacy & Security
- Protection Agent guidance is generated in-memory per session turn.
- Zero raw audio, PCM bytes, or sensitive recommendation logs are permanently stored to disk.

## 9. Current Limitations
- Claim Verification and Official Source Verification belong to Phase 11.

## 10. Next Phase
- **Phase 11**: Claim Verification + Official Source Verification.

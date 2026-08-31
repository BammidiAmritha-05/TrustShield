# TrustShield AI Backend - Phase 11 Official Claim Verification & Authoritative Source Verification

## 1. Architecture Overview
The source of truth for official claim extraction, live/static source retrieval, and 1-to-1 provenance verification in TrustShield AI is located at:
- `D:\TrustShield\ai\claim_verification\claim_verifier.py` (`verify_official_claim`)
- `D:\TrustShield\ai\claim_verification\claim_extractor.py` (`extract_claims_and_jurisdiction`)
- `D:\TrustShield\ai\claim_verification\source_retriever.py` (`retrieve_official_source_info`)
- `D:\TrustShield\ai\claim_verification\live_retriever.py` (`fetch_live_official_source`)
- `D:\TrustShield\ai\claim_verification\source_validator.py` (`validate_official_url`)
- `D:\TrustShield\ai\claim_verification\source_registry.py` (`AUTHORITATIVE_REGISTRY`)
- `D:\TrustShield\ai\claim_verification\freshness.py` (`FreshnessStatus`, rate limiting, TTL caching)
- `D:\TrustShield\ai\claim_verification\claim_comparator.py` (`compare_live_claims`)

```text
 [ Conversation Text / Final Transcript ]
                   |
                   v (asyncio.to_thread)
       [ AIClaimVerificationAdapter ]
                   |
       [ verify_official_claim ]
       - Claim Extraction & Jurisdiction Disambiguation
       - Official Domain Allowlist HTTPS Fetching
       - Provenance Alignment & Evidence Tracking
       - 1-to-1 Claim Comparison
                   |
                   v
       EVENT: CLAIM_VERIFICATION
```

The backend adapter (`app/ai_adapter/claim.py`) wraps `verify_official_claim` and streams structured `CLAIM_VERIFICATION` events over WebSocket.

## 2. Mandatory Verification Status Invariants
> [!IMPORTANT]
> Verification statuses (`VERIFIED`, `NOT_VERIFIED`, `CONTRADICTED`, `NO_CLAIM_DETECTED`) represent factual alignment against official policy registries.
> They are **never** reinterpreted or renamed as "SAFE", "SCAM", or "FRAUD".

## 3. Absence of Evidence Invariant
> [!IMPORTANT]
> Retrieval failure or `NOT_VERIFIED` status explicitly retains the limitation: `"Search/retrieval failure does NOT imply false claim."` It is **never** treated as proof of fraud.

## 4. Verification Statuses

| Status | Description | Example Condition |
| :--- | :--- | :--- |
| `VERIFIED` | Claim is factually supported by authoritative Tier-1/Tier-2 source | Scheme exists and matches official registry DBT disbursement rules |
| `CONTRADICTED` | Claim explicitly violates official policy rules | Claim demands upfront fee or phone OTP for DBT government scheme |
| `NOT_VERIFIED` | Source retrieval failed or entity jurisdiction is ambiguous | Unregistered entity or HTTPS fetch failure |
| `NO_CLAIM_DETECTED` | Text contains no verifiable factual claims | Harmless conversational text |

## 5. Event Protocol (`CLAIM_VERIFICATION`)
```json
{
  "type": "CLAIM_VERIFICATION",
  "version": 1,
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": "2026-08-29T12:00:00.000000+00:00",
  "payload": {
    "status": "available",
    "entity": {
      "name": "PM KISAN",
      "type": "government_scheme",
      "jurisdiction": "Central",
      "ambiguity": false,
      "status": "VERIFIED"
    },
    "claims": [
      {
        "text": "Verification fee required to receive PM-KISAN instalment.",
        "status": "CONTRADICTED",
        "evidence": "Official policy explicitly forbids charging upfront processing fees or phone money transfers.",
        "confidence": 0.95,
        "evidence_origin": "STATIC_REGISTRY",
        "currentness": "CURRENT_SUPPORTED"
      }
    ],
    "action": {
      "type": "transfer_money",
      "status": "CONTRADICTED"
    },
    "sources": [
      {
        "url": "https://pmkisan.gov.in",
        "authority": "Pradhan Mantri Kisan Samman Nidhi Portal (Ministry of Agriculture)",
        "retrieved_at": "2026-08-29T12:00:00Z",
        "relevance": "Official policy summary: Instalment payouts are directly remitted via Aadhaar-seeded bank accounts...",
        "tier": "TIER_1",
        "source_type": "LIVE_OFFICIAL_SOURCE",
        "freshness": "FRESH",
        "evidence_origin": "LIVE_FETCH",
        "http_status": 200,
        "content_length_bytes": 14200
      }
    ],
    "verification": {
      "overall_status": "CONTRADICTED",
      "confidence": 0.95,
      "otp_context": "not_applicable"
    },
    "limitations": [
      "Entity existence in official registry does NOT prove caller identity or authenticity.",
      "Official policy of 'PM KISAN' stipulates disbursements are via DBT, and explicitly prohibits direct UPI/phone transfers."
    ]
  }
}
```

## 6. Strict Event Sequence Order
Every turn emits events strictly in sequence:
1. `SIGNAL_UPDATE` (Conversation Intelligence)
2. `RISK_UPDATE` (Hybrid Risk Engine)
3. `CLAIM_VERIFICATION` (Official Source Claim Verifier)
4. `PROTECTION_UPDATE` (Protection Agent Guidance)

## 7. Health Readiness
`GET /health` exposes readiness status across all 6 backend AI components:
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

## 8. Security & Privacy Safeguards
- **HTTPS & Domain Allowlist**: Enforces HTTPS scheme and Tier-1/Tier-2 domain allowlists (`.gov.in`, `.nic.in`, `bank.sbi`, `hdfcbank.com`, `rbi.org.in`). Non-HTTPS or non-allowlisted domains return `403` status.
- **Payload Limits**: Max 500 KB payload size limit (`response.read(512000)`).
- **Anti-Prompt-Injection Safeguard**: Webpage content is sanitized to strip prompt-injection patterns (`sanitize_webpage_text_anti_prompt_injection`).
- **Rate Limiting & Caching**: Per-domain 1.0s cooldown and 300s TTL cache.
- **Privacy**: No raw audio, PCM bytes, or complete webpage text stored to disk. Extracted webpage text is truncated to concise 2,000-character snippets.

## 9. Current Limitations
- Final backend hardening, load testing, and production-readiness review belong to Phase 12.

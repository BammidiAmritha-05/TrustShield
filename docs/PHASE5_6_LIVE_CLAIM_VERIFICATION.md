# Phase 5.6: Live Official Source Verification Documentation

## Overview
Phase 5.6 upgrades TrustShield AI's **Official Claim Verification Engine** in `ai/claim_verification/` with real-time, controlled **Live Official Source Retrieval** (`LIVE_OFFICIAL_SOURCE`).

---

## 1. Security & Allowlist Architecture
- **HTTPS Only**: Rejects non-HTTPS schemes.
- **Domain Allowlist**: Restricts live fetching strictly to registered Tier-1/Tier-2 official domains (`*.gov.in`, `*.nic.in`, `bank.sbi`, `hdfcbank.com`, `rbi.org.in`).
- **Anti-Prompt-Injection**: Strips dangerous prompt-injection triggers from webpage content.
- **Read-Only**: Read-only GET requests with 3.0s timeout and 500 KB payload limits.

---

## 2. Sample Multi-Claim Output Schema

```json
{
  "entity": {
    "name": "Telangana Rythu Bharosa",
    "type": "government_scheme",
    "jurisdiction": "Telangana",
    "ambiguity": false,
    "status": "VERIFIED"
  },
  "claims": [
    {
      "text": "Telangana Rythu Bharosa payment/disbursement status notice.",
      "status": "VERIFIED",
      "evidence": "Official portal (https://rythubandhu.telangana.gov.in) confirms entity policy: Agricultural investment support is directly deposited into registered farmers' accounts via treasury DBT. Officials do not request OTP disclosure or phone fees.",
      "confidence": 0.85
    },
    {
      "text": "Processing fee or upfront money transfer is required to receive funds.",
      "status": "CONTRADICTED",
      "evidence": "Official policy explicitly forbids charging upfront processing fees or phone money transfers.",
      "confidence": 0.95
    }
  ],
  "action": {
    "type": "transfer_money",
    "status": "CONTRADICTED"
  },
  "sources": [
    {
      "url": "https://rythubandhu.telangana.gov.in",
      "authority": "Telangana Rythu Bandhu Portal (Department of Agriculture, Government of Telangana)",
      "retrieved_at": "2026-08-29T12:02:59Z",
      "relevance": "Official policy summary: Agricultural investment support is directly deposited into registered farmers' accounts via treasury DBT. Officials do not request OTP disclosure or phone fees.",
      "tier": "TIER_1",
      "source_type": "LIVE_OFFICIAL_SOURCE",
      "freshness": "FRESH"
    }
  ],
  "verification": {
    "overall_status": "CONTRADICTED",
    "confidence": 0.95,
    "otp_context": "not_applicable"
  },
  "limitations": [
    "Entity existence in official registry does NOT prove caller identity or authenticity.",
    "Official policy of 'Telangana Rythu Bharosa' stipulates disbursements are via DBT, and explicitly prohibits direct UPI/phone transfers."
  ]
}
```

---

## 3. Evaluation Benchmark Results Across 30 Test Scenarios

| # | Scenario | Entity | Ambiguity | Claims | Action Status | Overall Status | Test Result |
|---|----------|--------|-----------|--------|---------------|----------------|-------------|
| 1. Verified government claim | `PM KISAN` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 2. Verified bank claim | `SBI` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 3. Ambiguous scheme | `Rythu Bharosa` | `True` | `1` | `NONE` | `NOT_VERIFIED` | **PASSED** |
| 4. Unsupported scheme | `You Are Eligible For The Global Mega Fortune Subsidy Scheme` | `True` | `1` | `NONE` | `NOT_VERIFIED` | **PASSED** |
| 5. Current official claim | `YSR Rythu Bharosa` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 6. Stale official evidence | `PM KISAN` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 7. Source unavailable | `You Won The 2026 National Diamond Jubilee Lottery` | `True` | `1` | `NONE` | `NOT_VERIFIED` | **PASSED** |
| 8. Domain unavailable | `Calling From Quantum Web Services` | `True` | `1` | `NONE` | `NOT_VERIFIED` | **PASSED** |
| 9. Contradictory action | `YSR Rythu Bharosa` | `False` | `1` | `CONTRADICTED` | `CONTRADICTED` | **PASSED** |
| 10. Safe action | `Telangana Rythu Bharosa` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 11. Incoming OTP request | `SBI` | `False` | `1` | `CONTRADICTED` | `CONTRADICTED` | **PASSED** |
| 12. User-initiated OTP | `PM KISAN` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 13. Multiple claims | `Telangana Rythu Bharosa` | `False` | `2` | `CONTRADICTED` | `CONTRADICTED` | **PASSED** |
| 14. Conflicting claims | `Customs` | `False` | `1` | `CONTRADICTED` | `CONTRADICTED` | **PASSED** |
| 15. Unknown jurisdiction | `State Agricultural Subsidy` | `True` | `1` | `NOT_VERIFIED` | `NOT_VERIFIED` | **PASSED** |
| 16. Telangana Rythu Bharosa | `Telangana Rythu Bharosa` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 17. YSR Rythu Bharosa | `YSR Rythu Bharosa` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 18. PM-KISAN | `PM KISAN` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 19. Harmless sentence | `None` | `False` | `0` | `NONE` | `NO_CLAIM_DETECTED` | **PASSED** |
| 20. True claim + unverified caller | `YSR Rythu Bharosa` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 21. False/unsupported fee claim | `PM KISAN` | `False` | `2` | `CONTRADICTED` | `CONTRADICTED` | **PASSED** |
| 22. Courier/customs claim | `Customs` | `False` | `1` | `CONTRADICTED` | `CONTRADICTED` | **PASSED** |
| 23. Employer claim | `Employer` | `False` | `1` | `NOT_VERIFIED` | `NOT_VERIFIED` | **PASSED** |
| 24. Bank security claim | `HDFC Bank` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 25. Redirected source security test | `SBI` | `False` | `1` | `CONTRADICTED` | `CONTRADICTED` | **PASSED** |
| 26. Non-HTTPS URL security test | `SBI` | `False` | `1` | `CONTRADICTED` | `CONTRADICTED` | **PASSED** |
| 27. Untrusted blog domain test | `None` | `False` | `0` | `NONE` | `NO_CLAIM_DETECTED` | **PASSED** |
| 28. Malicious webpage text / prompt injection test | `YSR Rythu Bharosa` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 29. Source timeout test | `PM KISAN` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |
| 30. Stale-cache behavior test | `SBI` | `False` | `1` | `SUPPORTED` | `VERIFIED` | **PASSED** |

---

## 4. Test Suite Summary
- **Passed Scenarios**: `30 / 30` (`100%`)

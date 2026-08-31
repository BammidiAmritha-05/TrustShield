# Phase 2: Conversation Intelligence Engine & Audio Quality Gate Report

## Overview
Phase 2 implements TrustShield's structured conversation intelligence engine, answering:
> *"What is this interaction trying to make the user do, and how is it trying to influence them?"*

---

## 1. Phase 2A — Audio Quality Gate Improvements
- **Problem Resolved**: Pure white noise previously passed through AASIST-L and generated high spoof confidence while marked as `quality="good"`.
- **Solution**: Implemented spectral flatness (`spectral_flatness > 0.85`), RMS energy, and sample length checks in `ai/voice_authenticity/voice_authenticity_service.py`.
- **White Noise Test Result**:
```json
{
  "status": "insufficient_evidence",
  "reason": "unusable_audio",
  "spectral_flatness": 0.9913,
  "note": "Audio lacks speech structure and resembles unstructured white/colored noise."
}
```

---

## 2. Phase 2B — Conversation Intelligence Architecture

### Core Modules (`ai/intelligence/`)
- `schemas.py`: Schema data structures (`IntentResult`, `ActionResult`, `ManipulationResult`, `ImpersonationResult`, `ContextResult`, `ConversationAnalysisResult`).
- `intent_detector.py`: Intent categorization without immediate scam labelling.
- `action_detector.py`: Exact requested action extraction (`transfer_money`, `share_otp`, `install_remote_access`, etc.) and sensitivity classification.
- `manipulation_detector.py`: Quantitative scoring of social engineering tactics (urgency, secrecy, fear, authority pressure, etc.).
- `impersonation_detector.py`: Claimed identity extraction (`bank`, `police`, `family_member`, `executive`, etc.).
- `context_analyzer.py`: Session context builder.
- `conversation_intelligence.py`: Master orchestrator & plain-language explanation generator.

---

## 3. Test Cases & False Positive Evaluation

```json
{
  "1. Normal family conversation": {
    "input_text": "Hi Mom, how are you? Are we still meeting for dinner tonight at 8 PM?",
    "session_context": {
      "claimed_role": "family_member",
      "identity_verified": true
    },
    "analysis": {
      "intent": {
        "type": "harmless_conversation",
        "confidence": 0.9
      },
      "requested_action": {
        "type": "no_risky_action",
        "sensitivity": "none",
        "confidence": 0.9
      },
      "manipulation": {
        "urgency": 0.0,
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
        "possible_impersonation": false,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": true,
        "unusual_request": false,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves from a claimed identity of family member.",
      "latency_ms": 2.2
    }
  },
  "2. Family emergency money scam": {
    "input_text": "Dad, I got into a terrible accident in Mumbai and I'm at the hospital! Please transfer \u20b950,000 immediately to this doctor's UPI, don't tell mom!",
    "session_context": {
      "claimed_role": "family_member",
      "identity_verified": false
    },
    "analysis": {
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
        "emotional_pressure": 0.9,
        "threat": 0.0,
        "reward": 0.0,
        "isolation": 0.0,
        "intimidation": 0.0,
        "forced_compliance": 0.0
      },
      "impersonation": {
        "claimed_identity": "family_member",
        "possible_impersonation": true,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": false,
        "unusual_request": true,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves a request to transfer money combined with high urgency from a claimed identity of family member (unverified).",
      "latency_ms": 0.18
    }
  },
  "3. Bank OTP request": {
    "input_text": "Hello, this is SBI customer care. Your card is blocked. Please read out the 6-digit OTP sent to your phone right now to unblock.",
    "session_context": {
      "claimed_role": "bank",
      "identity_verified": false
    },
    "analysis": {
      "intent": {
        "type": "credential_theft",
        "confidence": 0.94
      },
      "requested_action": {
        "type": "share_otp",
        "sensitivity": "critical",
        "confidence": 0.98
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
        "claimed_identity": "bank",
        "possible_impersonation": true,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": false,
        "unusual_request": true,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves a request to share otp combined with high urgency from a claimed identity of bank (unverified).",
      "latency_ms": 0.14
    }
  },
  "4. Bank account verification": {
    "input_text": "Good morning, this is HDFC Bank routine verification. Please confirm if your registered address is 101 MG Road.",
    "session_context": {
      "claimed_role": "bank",
      "identity_verified": false
    },
    "analysis": {
      "intent": {
        "type": "harmless_conversation",
        "confidence": 0.9
      },
      "requested_action": {
        "type": "no_risky_action",
        "sensitivity": "none",
        "confidence": 0.9
      },
      "manipulation": {
        "urgency": 0.0,
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
        "claimed_identity": "bank",
        "possible_impersonation": true,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": false,
        "unusual_request": false,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves from a claimed identity of bank (unverified).",
      "latency_ms": 0.15
    }
  },
  "5. CEO payment request": {
    "input_text": "I am the CEO. I need you to execute an urgent wire transfer of \u20b95,00,000 for a confidential acquisition. Do not discuss with anyone in the office.",
    "session_context": {
      "claimed_role": "executive",
      "identity_verified": false
    },
    "analysis": {
      "intent": {
        "type": "financial_fraud",
        "confidence": 0.92
      },
      "requested_action": {
        "type": "transfer_money",
        "sensitivity": "critical",
        "confidence": 0.96
      },
      "manipulation": {
        "urgency": 0.96,
        "secrecy": 0.91,
        "fear": 0.0,
        "authority_pressure": 0.88,
        "emotional_pressure": 0.0,
        "threat": 0.0,
        "reward": 0.0,
        "isolation": 0.0,
        "intimidation": 0.0,
        "forced_compliance": 0.0
      },
      "impersonation": {
        "claimed_identity": "executive",
        "possible_impersonation": true,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": false,
        "unusual_request": true,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves a request to transfer money combined with high urgency, secrecy, authority pressure from a claimed identity of executive (unverified).",
      "latency_ms": 0.13
    }
  },
  "6. Remote-access scam": {
    "input_text": "Your computer has a virus. Download AnyDesk immediately and allow screen sharing access so tech support can fix it.",
    "session_context": {
      "claimed_role": "customer_support",
      "identity_verified": false
    },
    "analysis": {
      "intent": {
        "type": "remote_access",
        "confidence": 0.95
      },
      "requested_action": {
        "type": "install_remote_access",
        "sensitivity": "critical",
        "confidence": 0.98
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
        "claimed_identity": "customer_support",
        "possible_impersonation": true,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": false,
        "unusual_request": true,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves a request to install remote access combined with high urgency from a claimed identity of customer support (unverified).",
      "latency_ms": 0.07
    }
  },
  "7. Digital-arrest style threat": {
    "input_text": "This is Inspector Sharma from Delhi Cyber Crime. A legal warrant and CBI digital arrest has been issued against your Aadhaar card for money laundering. Do not disconnect this call!",
    "session_context": {
      "claimed_role": "police",
      "identity_verified": false
    },
    "analysis": {
      "intent": {
        "type": "financial_fraud",
        "confidence": 0.92
      },
      "requested_action": {
        "type": "share_identity_document",
        "sensitivity": "medium",
        "confidence": 0.87
      },
      "manipulation": {
        "urgency": 0.0,
        "secrecy": 0.0,
        "fear": 0.9,
        "authority_pressure": 0.88,
        "emotional_pressure": 0.0,
        "threat": 0.0,
        "reward": 0.0,
        "isolation": 0.0,
        "intimidation": 0.0,
        "forced_compliance": 0.0
      },
      "impersonation": {
        "claimed_identity": "police",
        "possible_impersonation": true,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": false,
        "unusual_request": false,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves a request to share identity document combined with fear or threat of penalty, authority pressure from a claimed identity of police (unverified).",
      "latency_ms": 0.12
    }
  },
  "8. Delivery/courier scam": {
    "input_text": "FedEx courier service: Your parcel containing illegal items has been seized by customs. Pay \u20b915,000 customs penalty immediately or face arrest.",
    "session_context": {
      "claimed_role": "delivery_service",
      "identity_verified": false
    },
    "analysis": {
      "intent": {
        "type": "financial_fraud",
        "confidence": 0.92
      },
      "requested_action": {
        "type": "transfer_money",
        "sensitivity": "critical",
        "confidence": 0.96
      },
      "manipulation": {
        "urgency": 0.96,
        "secrecy": 0.0,
        "fear": 0.9,
        "authority_pressure": 0.0,
        "emotional_pressure": 0.0,
        "threat": 0.0,
        "reward": 0.0,
        "isolation": 0.0,
        "intimidation": 0.0,
        "forced_compliance": 0.0
      },
      "impersonation": {
        "claimed_identity": "delivery_service",
        "possible_impersonation": true,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": false,
        "unusual_request": true,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves a request to transfer money combined with high urgency, fear or threat of penalty from a claimed identity of delivery service (unverified).",
      "latency_ms": 0.11
    }
  },
  "9. Genuine urgent conversation without a risky action (False Positive Test)": {
    "input_text": "Hurry up, we are late for the flight! Please pack your bags right now!",
    "session_context": {
      "claimed_role": "family_member",
      "identity_verified": true
    },
    "analysis": {
      "intent": {
        "type": "other",
        "confidence": 0.5
      },
      "requested_action": {
        "type": "no_risky_action",
        "sensitivity": "none",
        "confidence": 0.9
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
        "possible_impersonation": false,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": true,
        "unusual_request": false,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves high pressure tactics (high urgency) from a claimed identity of family member.",
      "latency_ms": 0.1
    }
  },
  "10. Suspicious conversation with no money request (False Positive Test)": {
    "input_text": "I am watching you from across the street. Stay quiet.",
    "session_context": {
      "claimed_role": "unknown",
      "identity_verified": false
    },
    "analysis": {
      "intent": {
        "type": "harmless_conversation",
        "confidence": 0.9
      },
      "requested_action": {
        "type": "no_risky_action",
        "sensitivity": "none",
        "confidence": 0.9
      },
      "manipulation": {
        "urgency": 0.0,
        "secrecy": 0.91,
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
        "claimed_identity": "unknown",
        "possible_impersonation": true,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": false,
        "unusual_request": false,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves high pressure tactics (secrecy).",
      "latency_ms": 0.1
    }
  },
  "11. Small dinner money request (False Positive Test)": {
    "input_text": "I need you to send \u20b9500 for dinner.",
    "session_context": {
      "claimed_role": "friend",
      "identity_verified": true
    },
    "analysis": {
      "intent": {
        "type": "payment_request",
        "confidence": 0.85
      },
      "requested_action": {
        "type": "transfer_money",
        "sensitivity": "critical",
        "confidence": 0.96
      },
      "manipulation": {
        "urgency": 0.0,
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
        "claimed_identity": "friend",
        "possible_impersonation": false,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": true,
        "unusual_request": false,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves a request to transfer money from a claimed identity of friend.",
      "latency_ms": 0.09
    }
  },
  "12. OTP self-device advisory (False Positive Test)": {
    "input_text": "Please send the OTP from your own phone to your own device.",
    "session_context": {
      "claimed_role": "system",
      "identity_verified": true
    },
    "analysis": {
      "intent": {
        "type": "information_request",
        "confidence": 0.85
      },
      "requested_action": {
        "type": "no_risky_action",
        "sensitivity": "none",
        "confidence": 0.95,
        "details": "Instruction to retain credential on user's own device / advisory against sharing."
      },
      "manipulation": {
        "urgency": 0.0,
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
        "claimed_identity": "system",
        "possible_impersonation": false,
        "confidence": 0.9
      },
      "context": {
        "identity_verified": true,
        "unusual_request": false,
        "independent_verification_available": true
      },
      "explanation": "The interaction involves an interaction involving information request from a claimed identity of system.",
      "latency_ms": 0.05
    }
  }
}
```

---

## 4. Key Limitations & Design Principles
- **No SCAM = TRUE Label**: Phase 2 strictly extracts structured interaction signals without issuing final risk verdicts.
- **Explainability**: Plain-language explanations are generated directly from structured JSON fields without model jargon.

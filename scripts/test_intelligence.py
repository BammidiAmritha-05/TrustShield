"""
CLI Test Suite for TrustShield Audio Quality Gate & Conversation Intelligence Engine (Phase 2).
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import json
import time
from ai.voice_authenticity.voice_authenticity_service import analyze_audio
from ai.intelligence import analyze_conversation


def main():
    print("=== STARTING PHASE 2 TEST SUITE ===\n")

    # PART 1: AUDIO QUALITY GATE VERIFICATION
    print("--- PART 1: AUDIO QUALITY GATE TESTS ---")
    audio_tests = [
        ("Real Speech", os.path.join("tests", "audio", "real_voice.wav")),
        ("Silence", os.path.join("tests", "audio", "silence.wav")),
        ("Short Audio", os.path.join("tests", "audio", "short.wav")),
        ("White Noise", os.path.join("tests", "audio", "noisy.wav")),
    ]

    audio_gate_results = {}
    for label, audio_path in audio_tests:
        if os.path.exists(audio_path):
            res = analyze_audio(audio_path)
            audio_gate_results[label] = res
            print(f"[{label:<12}] Status: {res.get('status'):<22} | Reason/Quality: {res.get('reason', res.get('quality'))}")
            if label == "White Noise":
                assert res.get("status") == "insufficient_evidence" and res.get("reason") == "unusable_audio", "FAILED: Noise must be rejected as unusable_audio!"
                print("  -> Noise Quality Gate Assertion: PASSED (Rejected white noise successfully)")

    # PART 2: CONVERSATION INTELLIGENCE TEST CASES
    print("\n--- PART 2: CONVERSATION INTELLIGENCE TEST CASES ---")

    test_cases = [
        (
            "1. Normal family conversation",
            "Hi Mom, how are you? Are we still meeting for dinner tonight at 8 PM?",
            {"claimed_role": "family_member", "identity_verified": True}
        ),
        (
            "2. Family emergency money scam",
            "Dad, I got into a terrible accident in Mumbai and I'm at the hospital! Please transfer ₹50,000 immediately to this doctor's UPI, don't tell mom!",
            {"claimed_role": "family_member", "identity_verified": False}
        ),
        (
            "3. Bank OTP request",
            "Hello, this is SBI customer care. Your card is blocked. Please read out the 6-digit OTP sent to your phone right now to unblock.",
            {"claimed_role": "bank", "identity_verified": False}
        ),
        (
            "4. Bank account verification",
            "Good morning, this is HDFC Bank routine verification. Please confirm if your registered address is 101 MG Road.",
            {"claimed_role": "bank", "identity_verified": False}
        ),
        (
            "5. CEO payment request",
            "I am the CEO. I need you to execute an urgent wire transfer of ₹5,00,000 for a confidential acquisition. Do not discuss with anyone in the office.",
            {"claimed_role": "executive", "identity_verified": False}
        ),
        (
            "6. Remote-access scam",
            "Your computer has a virus. Download AnyDesk immediately and allow screen sharing access so tech support can fix it.",
            {"claimed_role": "customer_support", "identity_verified": False}
        ),
        (
            "7. Digital-arrest style threat",
            "This is Inspector Sharma from Delhi Cyber Crime. A legal warrant and CBI digital arrest has been issued against your Aadhaar card for money laundering. Do not disconnect this call!",
            {"claimed_role": "police", "identity_verified": False}
        ),
        (
            "8. Delivery/courier scam",
            "FedEx courier service: Your parcel containing illegal items has been seized by customs. Pay ₹15,000 customs penalty immediately or face arrest.",
            {"claimed_role": "delivery_service", "identity_verified": False}
        ),
        (
            "9. Genuine urgent conversation without a risky action (False Positive Test)",
            "Hurry up, we are late for the flight! Please pack your bags right now!",
            {"claimed_role": "family_member", "identity_verified": True}
        ),
        (
            "10. Suspicious conversation with no money request (False Positive Test)",
            "I am watching you from across the street. Stay quiet.",
            {"claimed_role": "unknown", "identity_verified": False}
        ),
        (
            "11. Small dinner money request (False Positive Test)",
            "I need you to send ₹500 for dinner.",
            {"claimed_role": "friend", "identity_verified": True}
        ),
        (
            "12. OTP self-device advisory (False Positive Test)",
            "Please send the OTP from your own phone to your own device.",
            {"claimed_role": "system", "identity_verified": True}
        )
    ]

    intel_results = {}

    for title, text, session_ctx in test_cases:
        t_start = time.perf_counter()
        analysis = analyze_conversation(text, session_context=session_ctx)
        t_end = time.perf_counter()
        latency_ms = (t_end - t_start) * 1000

        res_dict = analysis.to_dict()
        res_dict["latency_ms"] = round(latency_ms, 2)
        intel_results[title] = {
            "input_text": text,
            "session_context": session_ctx,
            "analysis": res_dict
        }

        print(f"\n[{title}]")
        print(f"  Input        : \"{text}\"")
        print(f"  Intent       : {analysis.intent.type} (conf: {analysis.intent.confidence})")
        print(f"  Action       : {analysis.requested_action.type} (sens: {analysis.requested_action.sensitivity})")
        print(f"  Manipulation : Urgency={analysis.manipulation.urgency}, Secrecy={analysis.manipulation.secrecy}, Fear={analysis.manipulation.fear}")
        print(f"  Impersonation: {analysis.impersonation.claimed_identity} (possible: {analysis.impersonation.possible_impersonation})")
        print(f"  Context      : Verified={analysis.context.identity_verified}, Unusual={analysis.context.unusual_request}")
        print(f"  Explanation  : {analysis.explanation}")

    # Generate Markdown documentation in docs/PHASE2_CONVERSATION_INTELLIGENCE.md
    doc_path = os.path.join("docs", "PHASE2_CONVERSATION_INTELLIGENCE.md")
    os.makedirs("docs", exist_ok=True)

    doc_content = f"""# Phase 2: Conversation Intelligence Engine & Audio Quality Gate Report

## Overview
Phase 2 implements TrustShield's structured conversation intelligence engine, answering:
> *"What is this interaction trying to make the user do, and how is it trying to influence them?"*

---

## 1. Phase 2A — Audio Quality Gate Improvements
- **Problem Resolved**: Pure white noise previously passed through AASIST-L and generated high spoof confidence while marked as `quality="good"`.
- **Solution**: Implemented spectral flatness (`spectral_flatness > 0.85`), RMS energy, and sample length checks in `ai/voice_authenticity/voice_authenticity_service.py`.
- **White Noise Test Result**:
```json
{json.dumps(audio_gate_results.get('White Noise'), indent=2)}
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
{json.dumps(intel_results, indent=2)}
```

---

## 4. Key Limitations & Design Principles
- **No SCAM = TRUE Label**: Phase 2 strictly extracts structured interaction signals without issuing final risk verdicts.
- **Explainability**: Plain-language explanations are generated directly from structured JSON fields without model jargon.
"""

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc_content)

    print(f"\nSaved test report to {doc_path}")


if __name__ == "__main__":
    main()

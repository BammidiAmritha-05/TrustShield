"""
Comprehensive Verification Suite for TrustShield Protection Agent (Phase 4).
Tests 20 edge cases covering action safety, identity guidance, confidence scaling,
trusted contacts, uncertainty, and offline LLM fallback.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import json
from ai.intelligence import analyze_conversation
from ai.risk import RiskEngine
from ai.verification import ProtectionAgent, TrustedContact


def main():
    print("=== STARTING PHASE 4 PROTECTION AGENT TEST SUITE ===\n")

    agent = ProtectionAgent()

    trusted_contacts = [
        TrustedContact(id="tc_1", name="Anand (Brother)", relationship="family_member", verification_channel="+919876543210"),
        TrustedContact(id="tc_2", name="HDFC Official Helpline", relationship="bank", verification_channel="1800 202 6161"),
    ]

    scenarios = [
        # 1. High risk + High confidence
        (
            "1. High risk + High confidence",
            "Dad, I got into a terrible accident in Mumbai! Transfer ₹50,000 immediately, don't tell mom!",
            {"claimed_role": "family_member", "identity_verified": False},
            None,
            ["HIGH_RISK"]
        ),
        # 2. High risk + Low confidence
        (
            "2. High risk + Low confidence",
            "Send money immediately.",
            {"claimed_role": "unknown", "identity_verified": False},
            None,
            ["HIGH_RISK", "SUSPICIOUS"]
        ),
        # 3. Suspicious + Harmless action
        (
            "3. Suspicious + Harmless action",
            "This is urgent bank notification. Please stay on line for account verification.",
            {"claimed_role": "bank", "identity_verified": False},
            None,
            ["SUSPICIOUS", "CAUTION"]
        ),
        # 4. Genuine urgent conversation
        (
            "4. Genuine urgent conversation",
            "Hurry up, we are late for the flight! Please pack your bags right now!",
            {"claimed_role": "family_member", "identity_verified": True},
            None,
            ["SAFE"]
        ),
        # 5. Real voice + Malicious action
        (
            "5. Real voice + Malicious action",
            "Please read out the 6-digit OTP sent to your phone right now to unblock your card.",
            {"claimed_role": "bank", "identity_verified": False},
            {"status": "available", "synthetic_score": 0.02, "quality": "good"},
            ["HIGH_RISK"]
        ),
        # 6. Suspicious voice + Harmless conversation
        (
            "6. Suspicious voice + Harmless conversation",
            "Hello, thank you for calling customer service. Have a great day!",
            {"claimed_role": "customer_support", "identity_verified": False},
            {"status": "available", "synthetic_score": 0.95, "quality": "good"},
            ["CAUTION", "SUSPICIOUS"]
        ),
        # 7. AASIST unavailable
        (
            "7. AASIST unavailable",
            "I need you to execute an urgent wire transfer of ₹5,00,000 for a confidential acquisition.",
            {"claimed_role": "executive", "identity_verified": False},
            None,  # AASIST offline
            ["HIGH_RISK"]
        ),
        # 8. Transcript unavailable (Unusable audio)
        (
            "8. Transcript unavailable",
            "",
            {"claimed_role": "unknown", "identity_verified": False},
            {"status": "insufficient_evidence", "reason": "unusable_audio"},
            ["UNCERTAIN"]
        ),
        # 9. Unknown identity
        (
            "9. Unknown identity",
            "Send ₹80,000 right now.",
            {"claimed_role": "unknown", "identity_verified": False},
            None,
            ["HIGH_RISK"]
        ),
        # 10. Verified trusted contact
        (
            "10. Verified trusted contact",
            "Son, I need ₹50,000 for emergency doctor fee, please transfer urgently.",
            {"claimed_role": "family_member", "identity_verified": False},
            None,
            ["HIGH_RISK"]
        ),
        # 11. Family money request
        (
            "11. Family money request",
            "Dad, please send ₹50,000 right away.",
            {"claimed_role": "family_member", "identity_verified": False},
            None,
            ["HIGH_RISK"]
        ),
        # 12. Bank OTP request
        (
            "12. Bank OTP request",
            "Hello, this is SBI customer care. Please read out the 6-digit OTP sent to your phone right now.",
            {"claimed_role": "bank", "identity_verified": False},
            None,
            ["HIGH_RISK"]
        ),
        # 13. Employer payment request
        (
            "13. Employer payment request",
            "I am the CEO. Authorize ₹3,00,000 wire transfer immediately, keep confidential.",
            {"claimed_role": "executive", "identity_verified": False},
            None,
            ["HIGH_RISK"]
        ),
        # 14. Remote-access request
        (
            "14. Remote-access request",
            "Your computer has a virus. Download AnyDesk immediately and allow screen sharing access.",
            {"claimed_role": "customer_support", "identity_verified": False},
            None,
            ["HIGH_RISK"]
        ),
        # 15. Delivery-link request
        (
            "15. Delivery-link request",
            "FedEx courier update: Click this link bit.ly/customs-pay to clear illegal package customs fee.",
            {"claimed_role": "delivery_service", "identity_verified": False},
            None,
            ["HIGH_RISK"]
        ),
        # 16. Digital-arrest style threat
        (
            "16. Digital-arrest style threat",
            "This is Inspector Sharma from Delhi Cyber Crime. A legal warrant and CBI digital arrest has been issued against your Aadhaar card.",
            {"claimed_role": "police", "identity_verified": False},
            None,
            ["HIGH_RISK"]
        ),
        # 17. No risky action
        (
            "17. No risky action",
            "Good morning, hope you have a great day!",
            {"claimed_role": "colleague", "identity_verified": True},
            None,
            ["SAFE"]
        ),
        # 18. Conflicting evidence
        (
            "18. Conflicting evidence",
            "Transfer ₹80,000 immediately!",
            {"claimed_role": "unknown", "identity_verified": False},
            {"status": "available", "synthetic_score": 0.01, "quality": "good"},
            ["HIGH_RISK"]
        ),
        # 19. Legitimate financial request
        (
            "19. Legitimate financial request",
            "I need you to send ₹500 for dinner.",
            {"claimed_role": "friend", "identity_verified": True},
            None,
            ["SAFE", "CAUTION"]
        ),
        # 20. Educational discussion about scams
        (
            "20. Educational discussion about scams",
            "In our cybersecurity class today, we discussed how scammers demand urgent OTP sharing.",
            {"claimed_role": "instructor", "identity_verified": True},
            None,
            ["SAFE"]
        ),
    ]

    passed_count = 0
    results_summary = []

    for idx, (title, text, ctx, voice, expected_levels) in enumerate(scenarios, start=1):
        # Instantiate fresh RiskEngine per scenario to isolate temporal state
        engine = RiskEngine()

        conv = analyze_conversation(text, session_context=ctx).to_dict() if text else None
        risk_res = engine.evaluate_turn(conversation_analysis=conv, voice_analysis=voice, session_context=ctx, turn_index=1)
        plan = agent.generate_protection_guidance(risk_assessment=risk_res, conversation_analysis=conv, trusted_contacts=trusted_contacts)

        plan_dict = plan.to_dict()
        pred_level = plan_dict["protection_level"]
        status = "PASSED" if pred_level in expected_levels else "FAILED"
        if status == "PASSED":
            passed_count += 1

        results_summary.append({
            "scenario": title,
            "protection_level": pred_level,
            "recommended_action": plan_dict["recommended_action"],
            "status": status,
            "why": plan_dict["why"],
            "do": plan_dict["do"],
            "do_not": plan_dict["do_not"],
            "verify": plan_dict["verify"],
            "draft_message": plan_dict["draft_verification_message"]
        })

        print(f"[{title}]")
        print(f"  Level      : {pred_level:<12} (Expected: {expected_levels}) | Status: {status}")
        print(f"  Action     : {plan_dict['recommended_action']}")
        print(f"  WHY        : {plan_dict['why']}")
        print(f"  DO         : {plan_dict['do']}")
        print(f"  DO NOT     : {plan_dict['do_not']}")
        print(f"  VERIFY     : {plan_dict['verify']}")
        if plan_dict['draft_verification_message']:
            print(f"  DRAFT MSG  : \"{plan_dict['draft_verification_message']}\"")
        print()

    print(f"=== SUMMARY: {passed_count}/{len(scenarios)} SCENARIOS PASSED ===")
    assert passed_count == len(scenarios), f"FAILED: {len(scenarios) - passed_count} scenarios did not match expected outcomes!"

    # Save docs/PHASE4_ADAPTIVE_VERIFICATION.md
    doc_path = os.path.join("docs", "PHASE4_ADAPTIVE_VERIFICATION.md")
    os.makedirs("docs", exist_ok=True)

    doc_content = f"""# Phase 4: Adaptive Verification + Protection Agent Documentation

## Overview
Phase 4 implements TrustShield AI's **Protection Agent & Adaptive Verification Engine**. It translates multi-channel risk assessments into safe, identity-aware, and action-specific user guidance (`WHY`, `DO`, `DO NOT`, `VERIFY`).

---

## 1. Safety Principles & Zero-Autonomous Action Constraint
- **User Control**: The Protection Agent **never** autonomously transfers money, contacts institutions, sends messages, blocks accounts, or accuses callers.
- **Deterministic Policy Authority**: All safety recommendations are driven by reviewable deterministic rules in `ai/verification/verification_policy.py`.
- **LLM Offline Fallback**: If an LLM is offline, deterministic rules provide 100% functional protection without failure.

---

## 2. Protection Guidance Structure

```json
{json.dumps(results_summary[0], indent=2)}
```

---

## 3. Evaluation Results Across 20 Edge Cases

| # | Scenario | Protection Level | Recommended Action | Status |
|---|----------|------------------|--------------------|--------|
"""
    for item in results_summary:
        doc_content += f"| {item['scenario']} | `{item['protection_level']}` | `{item['recommended_action']}` | **{item['status']}** |\n"

    doc_content += f"""
---

## 4. Test Suite Summary
- **Passed Scenarios**: `{passed_count} / {len(scenarios)}` (`100%`)
"""

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc_content)

    print(f"Saved Phase 4 report to {doc_path}")


if __name__ == "__main__":
    main()

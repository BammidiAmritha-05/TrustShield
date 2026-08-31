"""
Unit & Integration Verification Script for TrustShield Risk Engine (Phase 3).
Tests temporal evidence accumulation, contradiction handling, paraphrase stability, and model independence.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import json
from ai.risk import RiskEngine, RiskLevel
from ai.intelligence import analyze_conversation


def main():
    print("=== STARTING RISK ENGINE VERIFICATION SUITE ===\n")

    # TEST 1: TEMPORAL EVIDENCE ACCUMULATION ACROSS TURNS (T1 -> T4)
    print("--- TEST 1: TEMPORAL EVIDENCE ACCUMULATION ---")
    engine = RiskEngine()

    turns = [
        ("T1: Greeting", "Hi Dad, how are you?", {"claimed_role": "family_member", "identity_verified": False}),
        ("T2: Problem Statement", "I got into a terrible accident in Mumbai and I am stuck at the hospital!", {"claimed_role": "family_member", "identity_verified": False}),
        ("T3: Secrecy Added", "Don't tell mom or anyone else in the family right now!", {"claimed_role": "family_member", "identity_verified": False}),
        ("T4: Financial Request", "Please transfer ₹50,000 immediately to this doctor's UPI account!", {"claimed_role": "family_member", "identity_verified": False}),
    ]

    for turn_num, (label, text, ctx) in enumerate(turns, start=1):
        conv = analyze_conversation(text, session_context=ctx).to_dict()
        res = engine.evaluate_turn(conversation_analysis=conv, session_context=ctx, turn_index=turn_num)
        print(f"[{label}] Risk Index: {res.get('risk_index'):<3} | Level: {res.get('risk_level'):<10} | Confidence: {res.get('confidence')}")

    print("  -> Temporal Timeline:")
    print(json.dumps(engine.temporal_engine.get_timeline(), indent=2))
    assert res.get("risk_level") == RiskLevel.HIGH_RISK.value, "FAILED: Turn 4 must escalate to HIGH_RISK!"
    print("  -> Temporal Accumulation Test: PASSED\n")

    # TEST 2: CONTRADICTION HANDLING
    print("--- TEST 2: CONTRADICTION HANDLING ---")
    # Scenario A: Genuine Voice + Suspicious Intent
    engine_contra_a = RiskEngine()
    conv_a = analyze_conversation("Send ₹80,000 immediately, do not tell anyone!", session_context={"claimed_role": "unknown", "identity_verified": False}).to_dict()
    voice_a = {"status": "available", "synthetic_score": 0.04, "bona_fide_score": 1.85, "quality": "good"}
    res_a = engine_contra_a.evaluate_turn(conversation_analysis=conv_a, voice_analysis=voice_a, turn_index=1)
    print(f"[Genuine Voice + Suspicious Intent] Level: {res_a.get('risk_level')} | Risk Index: {res_a.get('risk_index')}")
    assert res_a.get("risk_level") == RiskLevel.HIGH_RISK.value, "FAILED: Suspicious intent must maintain high concern!"

    # Scenario B: Synthetic Voice + Harmless Conversation
    engine_contra_b = RiskEngine()
    conv_b = analyze_conversation("Hello, thank you for calling customer service. Have a wonderful day!", session_context={"claimed_role": "customer_support", "identity_verified": False}).to_dict()
    voice_b = {"status": "available", "synthetic_score": 0.95, "bona_fide_score": -1.56, "quality": "good"}
    res_b = engine_contra_b.evaluate_turn(conversation_analysis=conv_b, voice_analysis=voice_b, turn_index=1)
    print(f"[Synthetic Voice + Harmless Conversation] Level: {res_b.get('risk_level')} | Risk Index: {res_b.get('risk_index')}")
    assert res_b.get("risk_level") in [RiskLevel.CAUTION.value, RiskLevel.SUSPICIOUS.value], "FAILED: Synthetic voice + harmless conversation must flag CAUTION/SUSPICIOUS!"
    print("  -> Contradiction Handling Test: PASSED\n")

    # TEST 3: PARAPHRASE STABILITY TEST
    print("--- TEST 3: PARAPHRASE STABILITY TEST ---")
    paraphrases = [
        "Send ₹80,000 right now.",
        "Please transfer eighty thousand immediately.",
        "Can you authorize the ₹80K payment urgently?",
        "I need you to execute an immediate transfer of 80000 rupees."
    ]

    para_results = []
    for p_text in paraphrases:
        eng_p = RiskEngine()
        conv_p = analyze_conversation(p_text, session_context={"claimed_role": "unknown", "identity_verified": False}).to_dict()
        res_p = eng_p.evaluate_turn(conversation_analysis=conv_p, turn_index=1)
        para_results.append(res_p.get("risk_level"))
        print(f"  Input: \"{p_text}\" -> Level: {res_p.get('risk_level')}, Index: {res_p.get('risk_index')}")

    assert len(set(para_results)) == 1 and para_results[0] == RiskLevel.HIGH_RISK.value, "FAILED: All paraphrases must produce HIGH_RISK!"
    print("  -> Paraphrase Stability Test: PASSED\n")

    # TEST 4: MODEL INDEPENDENCE & GRACEFUL DEGRADATION
    print("--- TEST 4: MODEL INDEPENDENCE (AASIST-L Offline) ---")
    eng_offline = RiskEngine()
    conv_off = analyze_conversation("Please read out the 6-digit OTP sent to your phone right now.", session_context={"claimed_role": "bank", "identity_verified": False}).to_dict()
    # Evaluate with voice_analysis = None (AASIST-L offline)
    res_off = eng_offline.evaluate_turn(conversation_analysis=conv_off, voice_analysis=None, turn_index=1)
    print(f"[AASIST-L Offline] Level: {res_off.get('risk_level')}, Index: {res_off.get('risk_index')}, Confidence: {res_off.get('confidence')}")
    assert res_off.get("risk_level") in [RiskLevel.HIGH_RISK.value, RiskLevel.SUSPICIOUS.value], "FAILED: Engine must operate cleanly without voice model!"
    print("  -> Model Independence Test: PASSED\n")

    print("=== ALL RISK ENGINE TESTS COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()

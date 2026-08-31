"""
Full Benchmark & Evaluation Harness Script for TrustShield Risk Engine (Phase 3).
Evaluates Development Set (35 scenarios) and Holdout Test Set (15 scenarios).
Generates docs/PHASE3_HYBRID_RISK_ENGINE.md.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import json
from ai.evaluation import DEV_SCENARIOS, HOLDOUT_SCENARIOS, run_evaluation_suite


def main():
    print("=== STARTING TRUSTSHIELD PHASE 3 EVALUATION HARNESS ===\n")

    # 1. Run Development Set Evaluation
    print("--- 1. EVALUATING DEVELOPMENT SET (35 Scenarios) ---")
    dev_results = run_evaluation_suite(DEV_SCENARIOS, suite_name="Development Set (35 Scenarios)")
    dev_m = dev_results["metrics"]
    print(f"Total Scenarios : {dev_results['total_scenarios']}")
    print(f"TP: {dev_results['true_positives']} | FP: {dev_results['false_positives']} | TN: {dev_results['true_negatives']} | FN: {dev_results['false_negatives']} | Abstentions: {dev_results['abstentions']}")
    print(f"Precision       : {dev_m['precision']:.4f}")
    print(f"Recall          : {dev_m['recall']:.4f}")
    print(f"F1 Score        : {dev_m['f1_score']:.4f}")
    print(f"FPR             : {dev_m['false_positive_rate']:.4f}")
    print(f"FNR             : {dev_m['false_negative_rate']:.4f}")
    print(f"Coverage        : {dev_m['coverage']:.4f}")
    print(f"Abstention Rate : {dev_m['abstention_rate']:.4f}\n")

    # 2. Run Holdout Test Set Evaluation
    print("--- 2. EVALUATING UNTOUCHED HOLDOUT TEST SET (15 Scenarios) ---")
    holdout_results = run_evaluation_suite(HOLDOUT_SCENARIOS, suite_name="Holdout Test Set (15 Scenarios)")
    hold_m = holdout_results["metrics"]
    print(f"Total Scenarios : {holdout_results['total_scenarios']}")
    print(f"TP: {holdout_results['true_positives']} | FP: {holdout_results['false_positives']} | TN: {holdout_results['true_negatives']} | FN: {holdout_results['false_negatives']} | Abstentions: {holdout_results['abstentions']}")
    print(f"Precision       : {hold_m['precision']:.4f}")
    print(f"Recall          : {hold_m['recall']:.4f}")
    print(f"F1 Score        : {hold_m['f1_score']:.4f}")
    print(f"FPR             : {hold_m['false_positive_rate']:.4f}")
    print(f"FNR             : {hold_m['false_negative_rate']:.4f}")
    print(f"Coverage        : {hold_m['coverage']:.4f}")
    print(f"Abstention Rate : {hold_m['abstention_rate']:.4f}\n")

    # 3. Generate Markdown Documentation docs/PHASE3_HYBRID_RISK_ENGINE.md
    doc_path = os.path.join("docs", "PHASE3_HYBRID_RISK_ENGINE.md")
    os.makedirs("docs", exist_ok=True)

    doc_content = f"""# Phase 3: Hybrid TrustShield Evidence Engine Documentation & Evaluation Report

## Overview
Phase 3 implements the core **Hybrid Evidence & Risk Engine** for TrustShield AI. It fuses multi-channel evidence streams (voice authenticity, conversation intent, requested action, manipulation tactics, impersonation claims, and session context) across time to compute a transparent **Risk Index (0–100)** and independent **Evidence Confidence Score (0.0–1.0)**.

---

## 1. System Architecture & Evidence Schema

### Normalized Evidence Object
Every evidence item is normalized across modules:
```json
{{
  "evidence_id": "a1b2c3d4",
  "signal": "requested_action",
  "value": "transfer_money",
  "confidence": 0.96,
  "source": "ACTION",
  "timestamp": 1788001800.0,
  "reliability": 0.95,
  "turn_index": 1
}}
```

### Risk Index Policy Bands
- **SAFE** (`0 – 29`): Normal interaction, no risky action requested.
- **CAUTION** (`30 – 59`): Low-to-medium concern; minor pressure or unverified identity without critical requested action.
- **SUSPICIOUS** (`60 – 79`): High concern; risky action or unverified identity combined with manipulation tactics.
- **HIGH_RISK** (`80 – 100`): Critical threat level; dangerous action (money transfer, OTP, remote access) combined with urgency, secrecy, or extortion.
- **UNCERTAIN**: Insufficient evidence, audio quality gate rejection, or low confidence (< 0.35).

---

## 2. Safety Policy Floor Rules
- **POL_001 (Unverified OTP Request)**: Minimum Risk Floor = `75.0` (`SUSPICIOUS`).
- **POL_002 (Urgent Secret Money Transfer)**: Minimum Risk Floor = `82.0` (`HIGH_RISK`).
- **POL_003 (Remote Access Support Scam)**: Minimum Risk Floor = `85.0` (`HIGH_RISK`).
- **POL_004 (Law Enforcement Coercion)**: Minimum Risk Floor = `80.0` (`HIGH_RISK`).

---

## 3. Benchmark Evaluation Results

### A. Development Set Evaluation (35 Scenarios)
- **Total Scenarios**: `{dev_results['total_scenarios']}`
- **True Positives**: `{dev_results['true_positives']}` | **False Positives**: `{dev_results['false_positives']}`
- **True Negatives**: `{dev_results['true_negatives']}` | **False Negatives**: `{dev_results['false_negatives']}`
- **Abstentions**: `{dev_results['abstentions']}`
- **Precision**: `{dev_m['precision']:.4f}`
- **Recall**: `{dev_m['recall']:.4f}`
- **F1-Score**: `{dev_m['f1_score']:.4f}`
- **False Positive Rate (FPR)**: `{dev_m['false_positive_rate']:.4f}`
- **False Negative Rate (FNR)**: `{dev_m['false_negative_rate']:.4f}`
- **Coverage**: `{dev_m['coverage']:.4f}`
- **Abstention Rate**: `{dev_m['abstention_rate']:.4f}`

### B. Holdout Test Set Evaluation (15 Untouched Scenarios)
- **Total Scenarios**: `{holdout_results['total_scenarios']}`
- **True Positives**: `{holdout_results['true_positives']}` | **False Positives**: `{holdout_results['false_positives']}`
- **True Negatives**: `{holdout_results['true_negatives']}` | **False Negatives**: `{holdout_results['false_negatives']}`
- **Abstentions**: `{holdout_results['abstentions']}`
- **Precision**: `{hold_m['precision']:.4f}`
- **Recall**: `{hold_m['recall']:.4f}`
- **F1-Score**: `{hold_m['f1_score']:.4f}`
- **False Positive Rate (FPR)**: `{hold_m['false_positive_rate']:.4f}`
- **False Negative Rate (FNR)**: `{hold_m['false_negative_rate']:.4f}`
- **Coverage**: `{hold_m['coverage']:.4f}`
- **Abstention Rate**: `{hold_m['abstention_rate']:.4f}`

---

## 4. Key Design Principles & Limitations
1. **Model Independence**: Operates seamlessly even when AASIST-L voice model or LLM is offline.
2. **Overfitting Protection**: Semantic pattern matching ensures paraphrases (e.g. *"transfer 80K"*, *"send ₹80,000"*, *"authorize payment"*) map to identical risk outcomes.
3. **Traceability**: Every risk decision provides an audit trace of contributing signals and policy floor triggers.
"""

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc_content)

    print(f"Saved evaluation report to {doc_path}")


if __name__ == "__main__":
    main()

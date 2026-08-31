# Phase 3: Hybrid TrustShield Evidence Engine Documentation & Evaluation Report

## Overview
Phase 3 implements the core **Hybrid Evidence & Risk Engine** for TrustShield AI. It fuses multi-channel evidence streams (voice authenticity, conversation intent, requested action, manipulation tactics, impersonation claims, and session context) across time to compute a transparent **Risk Index (0–100)** and independent **Evidence Confidence Score (0.0–1.0)**.

---

## 1. System Architecture & Evidence Schema

### Normalized Evidence Object
Every evidence item is normalized across modules:
```json
{
  "evidence_id": "a1b2c3d4",
  "signal": "requested_action",
  "value": "transfer_money",
  "confidence": 0.96,
  "source": "ACTION",
  "timestamp": 1788001800.0,
  "reliability": 0.95,
  "turn_index": 1
}
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
- **Total Scenarios**: `35`
- **True Positives**: `14` | **False Positives**: `0`
- **True Negatives**: `17` | **False Negatives**: `2`
- **Abstentions**: `2`
- **Precision**: `1.0000`
- **Recall**: `0.8750`
- **F1-Score**: `0.9333`
- **False Positive Rate (FPR)**: `0.0000`
- **False Negative Rate (FNR)**: `0.1250`
- **Coverage**: `0.9429`
- **Abstention Rate**: `0.0571`

### B. Holdout Test Set Evaluation (15 Untouched Scenarios)
- **Total Scenarios**: `15`
- **True Positives**: `6` | **False Positives**: `0`
- **True Negatives**: `6` | **False Negatives**: `1`
- **Abstentions**: `2`
- **Precision**: `1.0000`
- **Recall**: `0.8571`
- **F1-Score**: `0.9231`
- **False Positive Rate (FPR)**: `0.0000`
- **False Negative Rate (FNR)**: `0.1429`
- **Coverage**: `0.8667`
- **Abstention Rate**: `0.1333`

---

## 4. Key Design Principles & Limitations
1. **Model Independence**: Operates seamlessly even when AASIST-L voice model or LLM is offline.
2. **Overfitting Protection**: Semantic pattern matching ensures paraphrases (e.g. *"transfer 80K"*, *"send ₹80,000"*, *"authorize payment"*) map to identical risk outcomes.
3. **Traceability**: Every risk decision provides an audit trace of contributing signals and policy floor triggers.

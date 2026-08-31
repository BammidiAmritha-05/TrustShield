"""
Evaluation Harness for TrustShield Risk Engine (Phase 3).
Calculates Precision, Recall, F1, FPR, FNR, Coverage, and Abstention Rate.
"""

from typing import List, Dict, Any
from ai.intelligence import analyze_conversation
from ai.risk import RiskEngine, RiskLevel


def run_evaluation_suite(scenarios: List[Dict[str, Any]], suite_name: str = "Evaluation Suite") -> Dict[str, Any]:
    """Runs a scenario dataset through TrustShield Risk Engine and computes evaluation metrics.

    Args:
        scenarios: List of scenario dictionaries.
        suite_name: Display name for the suite (e.g. 'Development Set' or 'Holdout Set').

    Returns:
        Dict containing comprehensive evaluation metrics and detailed scenario results.
    """
    total_scenarios = len(scenarios)
    tp = 0  # True Positives (High Risk / Suspicious correctly identified)
    fp = 0  # False Positives (Safe/Benign flagged as High Risk / Suspicious)
    tn = 0  # True Negatives (Safe/Benign correctly identified as Safe/Caution)
    fn = 0  # False Negatives (High Risk / Suspicious missed as Safe/Caution)
    abstentions = 0  # UNCERTAIN states

    scenario_results = []
    category_counts: Dict[str, Dict[str, int]] = {}

    for sc in scenarios:
        sc_id = sc.get("id")
        cat = sc.get("category", "General")
        text = sc.get("text", "")
        session_ctx = sc.get("session_context")
        voice_analysis = sc.get("voice_analysis")
        expected_level = sc.get("expected_risk_level")

        # Instantiate fresh RiskEngine per scenario to isolate temporal state
        engine = RiskEngine()

        conv_analysis = analyze_conversation(text, session_context=session_ctx).to_dict() if text else None
        eval_res = engine.evaluate_turn(
            conversation_analysis=conv_analysis,
            voice_analysis=voice_analysis,
            session_context=session_ctx,
            turn_index=1
        )

        pred_level = eval_res.get("risk_level")
        pred_index = eval_res.get("risk_index")
        confidence = eval_res.get("confidence")

        # Classification mapping:
        # High Risk / Suspicious = Positive class (Threat detected)
        # Safe / Caution = Negative class (Benign/Low concern)
        is_expected_positive = expected_level in ["HIGH_RISK", "SUSPICIOUS"]
        is_pred_positive = pred_level in ["HIGH_RISK", "SUSPICIOUS"]

        if pred_level == RiskLevel.UNCERTAIN.value:
            abstentions += 1
            match_status = "ABSTAIN"
        elif is_expected_positive and is_pred_positive:
            tp += 1
            match_status = "TP"
        elif not is_expected_positive and is_pred_positive:
            fp += 1
            match_status = "FP"
        elif not is_expected_positive and not is_pred_positive:
            tn += 1
            match_status = "TN"
        else:  # is_expected_positive and not is_pred_positive
            fn += 1
            match_status = "FN"

        if cat not in category_counts:
            category_counts[cat] = {"total": 0, "correct": 0}
        category_counts[cat]["total"] += 1
        if match_status in ["TP", "TN"] or (expected_level == pred_level):
            category_counts[cat]["correct"] += 1

        scenario_results.append({
            "id": sc_id,
            "category": cat,
            "text": text,
            "expected_level": expected_level,
            "predicted_level": pred_level,
            "risk_index": pred_index,
            "confidence": confidence,
            "match_status": match_status,
            "explanation": eval_res.get("explanation")
        })

    evaluable_count = total_scenarios - abstentions
    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 1.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 1.0
    f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0
    fpr = round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0.0
    fnr = round(fn / (fn + tp), 4) if (fn + tp) > 0 else 0.0
    coverage = round(evaluable_count / total_scenarios, 4) if total_scenarios > 0 else 1.0
    abstention_rate = round(abstentions / total_scenarios, 4) if total_scenarios > 0 else 0.0

    return {
        "suite_name": suite_name,
        "total_scenarios": total_scenarios,
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "abstentions": abstentions,
        "metrics": {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "false_positive_rate": fpr,
            "false_negative_rate": fnr,
            "coverage": coverage,
            "abstention_rate": abstention_rate
        },
        "category_accuracy": {cat: round(data["correct"] / data["total"], 2) for cat, data in category_counts.items()},
        "scenario_results": scenario_results
    }

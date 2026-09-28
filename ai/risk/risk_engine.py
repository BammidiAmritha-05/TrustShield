"""
Master Hybrid Risk Engine for TrustShield AI (Phase 3).
Combines multi-source evidence, action-centric scoring, context modifiers,
temporal accumulation, safety policy floors, and contradiction resolution.
"""

from typing import Dict, Any, Optional, List
from ai.evidence.evidence_schema import NormalizedEvidence, EvidenceSource
from ai.evidence.evidence_accumulator import EvidenceAccumulator
from ai.evidence.temporal_engine import TemporalEngine
from ai.risk.risk_thresholds import (
    RiskLevel,
    ACTION_SENSITIVITY_WEIGHTS,
    MANIPULATION_TACTIC_WEIGHTS,
    IMPERSONATION_BASE_WEIGHT,
    VOICE_AUTHENTICITY_MAX_WEIGHT,
    map_score_to_risk_level,
)
from ai.risk.confidence import calculate_confidence
from ai.risk.risk_policy import evaluate_safety_policies


class RiskEngine:
    """TrustShield Master Hybrid Risk Engine."""

    def __init__(self, temporal_engine: Optional[TemporalEngine] = None):
        self.accumulator = EvidenceAccumulator()
        self.temporal_engine = temporal_engine or TemporalEngine()

    def evaluate_turn(
    self,
        conversation_analysis: Optional[Dict[str, Any]] = None,
        voice_analysis: Optional[Dict[str, Any]] = None,
        claim_verification: Optional[Dict[str, Any]] = None,
        session_context: Optional[Dict[str, Any]] = None,
        turn_index: int = 1
    ) -> Dict[str, Any]:
        """Evaluates a single turn or session and returns the comprehensive TrustShield Risk Assessment.

        Args:
            conversation_analysis: Output dict from Conversation Intelligence analysis.
            voice_analysis: Output dict from AASIST-L Voice Authenticity analysis.
            session_context: Optional session metadata (identity_verified, etc.).
            turn_index: Interaction turn index.

        Returns:
            Dict containing risk_level, risk_index, confidence, explanation, trace, and policy violations.
        """
        # 1. Ingest Evidence
        turn_evidence: List[NormalizedEvidence] = []
        if voice_analysis:
            turn_evidence.extend(self.accumulator.ingest_voice_result(voice_analysis, turn_index=turn_index))
        if conversation_analysis:
            turn_evidence.extend(self.accumulator.ingest_conversation_result(conversation_analysis, turn_index=turn_index))

        if claim_verification:
            turn_evidence.extend(self.accumulator.ingest_claim_verification_result(claim_verification, turn_index=turn_index))

        all_evidence = self.accumulator.get_latest_evidence()

        # 2. Check for Unusable Audio / Abstention
        if voice_analysis and voice_analysis.get("status") == "insufficient_evidence" and not conversation_analysis:
            return {
                "risk_level": RiskLevel.UNCERTAIN.value,
                "risk_index": None,
                "confidence": 0.20,
                "reason": f"Insufficient audio evidence ({voice_analysis.get('reason')}).",
                "contributing_signals": [],
                "evidence_trace": [item.to_dict() for item in turn_evidence],
                "safety_policy_violations": [],
            }

        # 3. Calculate Base Score Components across accumulated session evidence
        raw_score = 0.0
        contributing_signals = []

        # A. Action Sensitivity Score
        actions = [item for item in all_evidence if item.signal == "requested_action"]
        if actions:
            latest_act_type = actions[-1].value
            act_info = conversation_analysis.get("requested_action", {}) if conversation_analysis else {}
            act_sens = act_info.get("sensitivity") if act_info.get("type") == latest_act_type else ("critical" if latest_act_type in ["transfer_money", "share_otp", "share_password", "install_remote_access"] else "high")
            act_pts = ACTION_SENSITIVITY_WEIGHTS.get(act_sens, 0.0)
            if act_pts > 0:
                raw_score += act_pts
                contributing_signals.append({
                    "signal": "requested_action",
                    "value": latest_act_type,
                    "points": act_pts,
                    "source": "ACTION"
                })
        else:
            act_sens = "none"

        # B. Manipulation Tactics Score (Accumulated max scores)
        tactic_maxes: Dict[str, float] = {}
        for item in all_evidence:
            if item.signal.startswith("manipulation_") and isinstance(item.value, (int, float)):
                tactic_name = item.signal.replace("manipulation_", "")
                tactic_maxes[tactic_name] = max(tactic_maxes.get(tactic_name, 0.0), item.value)

        for tactic, score in tactic_maxes.items():
            if score >= 0.50:
                base_w = MANIPULATION_TACTIC_WEIGHTS.get(tactic, 10.0)
                pts = base_w * score
                raw_score += pts
                contributing_signals.append({
                    "signal": f"manipulation_{tactic}",
                    "value": round(score, 2),
                    "points": round(pts, 2),
                    "source": "MANIPULATION"
                })

        # C. Impersonation & Identity Context Score
        identities = [item for item in all_evidence if item.signal == "claimed_identity" and item.value != "unknown"]
        identity_verified = any(item.value is True for item in all_evidence if item.signal == "identity_verified")

        if identities and not identity_verified:
            claimed_id = identities[-1].value
            pts = IMPERSONATION_BASE_WEIGHT
            raw_score += pts
            contributing_signals.append({
                "signal": "unverified_claimed_identity",
                "value": claimed_id,
                "points": pts,
                "source": "IMPERSONATION"
            })

        # D. Official Claim Verification Score
        verification_items = [
            item for item in all_evidence
            if item.signal == "claim_verification_status"]

        if verification_items:
            verification_status = verification_items[-1].value
            verification_confidence = verification_items[-1].confidence

            if verification_status == "CONTRADICTED":
                pts = 25.0 * verification_confidence
                raw_score += pts

                contributing_signals.append({
                    "signal": "claim_verification_contradicted",
                    "value": verification_status,
                    "points": round(pts, 2),
                    "source": "CLAIM_VERIFICATION"
                })

            elif verification_status == "NOT_VERIFIED":
                contributing_signals.append({
                    "signal": "claim_verification_unverified",
                    "value": verification_status,
                    "points": 0.0,
                    "source": "CLAIM_VERIFICATION"
                })

            elif verification_status == "VERIFIED":
                contributing_signals.append({
                    "signal": "claim_verification_verified",
                    "value": verification_status,
                    "points": 0.0,
                    "source": "CLAIM_VERIFICATION"
                })

        # E. Voice Authenticity Score (if available)
        voice_pts = 0.0
        if voice_analysis and voice_analysis.get("status") == "available":
            synth_score = voice_analysis.get("synthetic_score", 0.0)
            if synth_score > 0.40:
                voice_pts = synth_score * VOICE_AUTHENTICITY_MAX_WEIGHT
                raw_score += voice_pts
                contributing_signals.append({
                    "signal": "synthetic_voice_detected",
                    "value": round(synth_score, 4),
                    "points": round(voice_pts, 2),
                    "source": "VOICE_MODEL"
                })

        # F. Context Modifiers (Trusted Relationship / Low Risk Action Reductions)
        if identity_verified and act_sens in ["none", "low"]:
            raw_score = max(0.0, raw_score - 30.0)

        # 4. Temporal Accumulation
        instantaneous_score = min(100.0, raw_score)
        temporal_score = self.temporal_engine.update(
            instantaneous_risk=instantaneous_score,
            turn_index=turn_index,
            evidence_count=len(all_evidence)
        )

        # 5. Evaluate Safety Floor Policies
        floor_score, violations = evaluate_safety_policies(conversation_analysis or {}, all_evidence)
        final_risk_score = max(temporal_score, floor_score)
        final_risk_score = round(min(100.0, max(0.0, final_risk_score)), 1)

        # 6. Calculate Confidence
        confidence = calculate_confidence(all_evidence)

        # 7. Contradiction Handling & Map Risk Band
        risk_level = map_score_to_risk_level(final_risk_score, confidence)

        # Contradiction Handling: Genuine Voice + Highly Suspicious Conversation
        if voice_analysis and voice_analysis.get("status") == "available":
            synth_score = voice_analysis.get("synthetic_score", 0.0)
            if synth_score < 0.10 and final_risk_score >= 80.0:
                contributing_signals.append({
                    "signal": "contradiction_genuine_voice_suspicious_intent",
                    "value": "Voice appears authentic, but conversation content carries critical risk.",
                    "points": 0.0,
                    "source": "RULE"
                })

        # 8. Generate Traceable Decision Explanation
        explanation_parts = []
        if violations:
            explanation_parts.append(f"Safety Policy Triggered ({violations[0].policy_id}): {violations[0].reason}")
        elif conversation_analysis and conversation_analysis.get("explanation"):
            explanation_parts.append(conversation_analysis["explanation"])
        else:
            explanation_parts.append(f"Risk score evaluated at {final_risk_score} based on accumulated evidence.")

        final_explanation = " ".join(explanation_parts)

        # Update latest timeline entry with final resolved risk_level and score
        timeline = self.temporal_engine.get_timeline()
        if timeline:
            timeline[-1]["risk_level"] = risk_level
            timeline[-1]["risk_index"] = int(round(final_risk_score)) if risk_level != RiskLevel.UNCERTAIN.value else None
            timeline[-1]["confidence"] = confidence

        return {
            "risk_level": risk_level,
            "risk_index": int(round(final_risk_score)) if risk_level != RiskLevel.UNCERTAIN.value else None,
            "confidence": confidence,
            "explanation": final_explanation,
            "contributing_signals": contributing_signals,
            "evidence_trace": [item.to_dict() for item in all_evidence],
            "safety_policy_violations": [v.to_dict() for v in violations],
            "temporal_timeline": timeline,
        }

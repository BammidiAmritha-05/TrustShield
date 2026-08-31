"""
Safety Policy Floor Rules for TrustShield Risk Engine (Phase 3).
Reviewable rules that enforce minimum risk floors for critical threat configurations.
"""

from typing import List, Dict, Any, Tuple
from ai.evidence.evidence_schema import NormalizedEvidence
from ai.risk.risk_thresholds import RiskLevel


class PolicyViolation:
    def __init__(self, policy_id: str, name: str, minimum_score: float, minimum_level: str, reason: str):
        self.policy_id = policy_id
        self.name = name
        self.minimum_score = minimum_score
        self.minimum_level = minimum_level
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "minimum_score": self.minimum_score,
            "minimum_level": self.minimum_level,
            "reason": self.reason,
        }


def evaluate_safety_policies(
    conv_analysis: Dict[str, Any],
    evidence_items: List[NormalizedEvidence]
) -> Tuple[float, List[PolicyViolation]]:
    """Evaluates explicit safety floor policy rules across accumulated session evidence.

    Args:
        conv_analysis: Dict output from conversation intelligence analysis.
        evidence_items: List of accumulated normalized evidence items.

    Returns:
        Tuple of (highest_minimum_score_floor, list_of_policy_violations).
    """
    violations: List[PolicyViolation] = []
    floor_score: float = 0.0

    # Extract aggregated signals from accumulated evidence
    actions = [item.value for item in evidence_items if item.signal == "requested_action"]
    intents = [item.value for item in evidence_items if item.signal == "intent_category"]
    identities = [item.value for item in evidence_items if item.signal == "claimed_identity"]

    urgency_scores = [item.value for item in evidence_items if item.signal == "manipulation_urgency" and isinstance(item.value, (int, float))]
    secrecy_scores = [item.value for item in evidence_items if item.signal == "manipulation_secrecy" and isinstance(item.value, (int, float))]
    fear_scores = [item.value for item in evidence_items if item.signal == "manipulation_fear" and isinstance(item.value, (int, float))]
    authority_scores = [item.value for item in evidence_items if item.signal == "manipulation_authority_pressure" and isinstance(item.value, (int, float))]

    max_urgency = max(urgency_scores) if urgency_scores else 0.0
    max_secrecy = max(secrecy_scores) if secrecy_scores else 0.0
    max_fear = max(fear_scores) if fear_scores else 0.0
    max_authority = max(authority_scores) if authority_scores else 0.0

    # Identity verification status
    identity_verified = False
    for item in evidence_items:
        if item.signal == "identity_verified" and item.value is True:
            identity_verified = True

    # Policy 1: OTP / Credential Request + Unverified Identity -> Minimum HIGH_RISK (80)
    if any(act in ["share_otp", "share_password", "share_verification_code"] for act in actions) and not identity_verified:
        v = PolicyViolation(
            policy_id="POL_001",
            name="Unverified OTP Request Policy",
            minimum_score=80.0,
            minimum_level=RiskLevel.HIGH_RISK.value,
            reason="Unverified caller requested OTP/credential disclosure."
        )
        violations.append(v)
        floor_score = max(floor_score, 80.0)

    # Policy 2: Financial Transfer / Payment Link + Urgency + Unverified Identity -> Minimum HIGH_RISK (82)
    if any(act in ["transfer_money", "click_link"] for act in actions) and (max_urgency >= 0.60 or "financial_fraud" in intents) and not identity_verified:
        v = PolicyViolation(
            policy_id="POL_002",
            name="Urgent Unverified Money Transfer Policy",
            minimum_score=82.0,
            minimum_level=RiskLevel.HIGH_RISK.value,
            reason="Financial transfer or payment link requested under urgency and unverified identity."
        )
        violations.append(v)
        floor_score = max(floor_score, 82.0)

    # Policy 3: Remote Access Tool Installation + Authority/Support Pressure -> Minimum HIGH_RISK (85)
    if "install_remote_access" in actions and (max_authority >= 0.60 or max_urgency >= 0.60 or "remote_access" in intents):
        v = PolicyViolation(
            policy_id="POL_003",
            name="Remote Access Support Scam Policy",
            minimum_score=85.0,
            minimum_level=RiskLevel.HIGH_RISK.value,
            reason="Remote desktop access requested under authority or urgency pressure."
        )
        violations.append(v)
        floor_score = max(floor_score, 85.0)

    # Policy 4: Digital Arrest / Extortion Threat -> Minimum HIGH_RISK (80)
    if "financial_fraud" in intents and max_fear >= 0.70 and (max_authority >= 0.60 or any(id_claim in ["police", "government"] for id_claim in identities)):
        v = PolicyViolation(
            policy_id="POL_004",
            name="Law Enforcement Coercion Policy",
            minimum_score=80.0,
            minimum_level=RiskLevel.HIGH_RISK.value,
            reason="Purported law enforcement officer demanding compliance under fear or threat."
        )
        violations.append(v)
        floor_score = max(floor_score, 80.0)

    return floor_score, violations

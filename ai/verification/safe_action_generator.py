"""
Safe Action & Explanation Generator for TrustShield AI (Phase 4).
Generates structured WHY, DO, DO NOT, and VERIFY blocks derived strictly from evidence.
"""

from typing import Dict, Any, List, Optional, Tuple
from ai.verification.verification_schema import GuidanceBlock, TrustedContact
from ai.verification.verification_policy import (
    ACTION_SAFETY_RULES,
    get_identity_verification_guidance,
)


def generate_guidance_blocks(
    risk_assessment: Dict[str, Any],
    conversation_analysis: Optional[Dict[str, Any]] = None,
    trusted_contacts: Optional[List[TrustedContact]] = None
) -> Tuple[GuidanceBlock, Optional[TrustedContact]]:
    """Generates structured WHY, DO, DO NOT, and VERIFY guidance blocks.

    Args:
        risk_assessment: Dict output from Phase 3 Risk Engine.
        conversation_analysis: Optional dict output from Phase 2 Conversation Intelligence.
        trusted_contacts: Optional user-provided trusted contacts.

    Returns:
        Tuple of (GuidanceBlock object, matched_trusted_contact_or_None).
    """
    risk_level = risk_assessment.get("risk_level", "SAFE")
    confidence = risk_assessment.get("confidence", 1.0)
    explanation = risk_assessment.get("explanation", "")
    violations = risk_assessment.get("safety_policy_violations", [])

    # Extract requested action and claimed identity
    action_info = conversation_analysis.get("requested_action", {}) if conversation_analysis else {}
    action_type = action_info.get("type", "no_risky_action")

    imp_info = conversation_analysis.get("impersonation", {}) if conversation_analysis else {}
    claimed_identity = imp_info.get("claimed_identity", "unknown")

    # 1. Generate WHY (Reason for concern)
    if risk_level == "UNCERTAIN":
        why = risk_assessment.get("reason", "Evidence is insufficient or audio quality is unusable to evaluate risk reliably.")
    elif risk_level == "SAFE":
        why = "No risky actions, high-pressure manipulation, or unverified identity claims were detected."
    elif violations:
        why = f"{violations[0].get('reason')} ({explanation})"
    elif explanation:
        why = explanation
    else:
        why = f"Interaction carries {risk_level} concern based on detected conversation signals."

    # Adjust WHY wording if confidence is low
    if confidence < 0.50 and risk_level not in ["SAFE", "UNCERTAIN"]:
        why = f"This interaction may be risky. We do not have enough reliable evidence to confirm it ({why})."

    # 2. Lookup Action Rules (DO & DO NOT)
    action_rule = ACTION_SAFETY_RULES.get(action_type, ACTION_SAFETY_RULES["no_risky_action"])

    if risk_level == "SAFE":
        do_action = "Continue your interaction while exercising standard digital awareness."
        do_not_action = "No specific restrictions required."
    else:
        do_action = action_rule["do"]
        do_not_action = action_rule["do_not"]

        # Dual Risk Guard: If action is share_otp and fee/money transfer context is also present
        if action_type == "share_otp" and conversation_analysis:
            text_context = str(conversation_analysis).lower()
            if any(w in text_context for w in ["fee", "pay", "transfer", "rupees", "rs", "₹", "deposit"]):
                do_not_action = f"{do_not_action} Do NOT pay any upfront processing fee or transfer funds."
                do_action = f"{do_action} Never pay upfront fees to claim funds or subsidies."

    # 3. Lookup Identity Verification (VERIFY)
    verify_guidance, matched_contact = get_identity_verification_guidance(claimed_identity, trusted_contacts)

    if risk_level == "SAFE":
        verify_action = "Standard verification channels are available if needed."
    else:
        verify_action = verify_guidance

    block = GuidanceBlock(
        why=why,
        do=do_action,
        do_not=do_not_action,
        verify=verify_action
    )

    return block, matched_contact

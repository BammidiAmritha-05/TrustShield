"""
Verification Planner for TrustShield AI (Phase 4).
Orchestrates risk assessment, action sensitivity, identity verification, and trusted circle context.
"""

from typing import Dict, Any, List, Optional
from ai.verification.verification_schema import (
    ProtectionLevel,
    VerificationPlan,
    TrustedContact,
)
from ai.verification.verification_policy import ACTION_SAFETY_RULES
from ai.verification.safe_action_generator import generate_guidance_blocks
from ai.verification.verification_message_generator import generate_draft_verification_message


class VerificationPlanner:
    """Plans identity-aware and action-specific protection plans."""

    def plan_verification(
        self,
        risk_assessment: Dict[str, Any],
        conversation_analysis: Optional[Dict[str, Any]] = None,
        trusted_contacts: Optional[List[TrustedContact]] = None
    ) -> VerificationPlan:
        """Generates a complete VerificationPlan.

        Args:
            risk_assessment: Output dict from Phase 3 Risk Engine.
            conversation_analysis: Optional output dict from Phase 2 Conversation Intelligence.
            trusted_contacts: Optional list of user-provided trusted contacts.

        Returns:
            Validated VerificationPlan instance.
        """
        risk_level = risk_assessment.get("risk_level", ProtectionLevel.SAFE.value)
        confidence = risk_assessment.get("confidence", 1.0)

        # Extract requested action and claimed identity
        action_info = conversation_analysis.get("requested_action", {}) if conversation_analysis else {}
        action_type = action_info.get("type", "no_risky_action")

        imp_info = conversation_analysis.get("impersonation", {}) if conversation_analysis else {}
        claimed_identity = imp_info.get("claimed_identity", "unknown")

        # Map protection level
        protection_level = risk_level

        # Recommended Action Directive
        action_rule = ACTION_SAFETY_RULES.get(action_type, ACTION_SAFETY_RULES["no_risky_action"])
        recommended_action = action_rule["recommended_action"] if risk_level != ProtectionLevel.SAFE.value else "NO_ACTION_REQUIRED"

        # Generate WHY, DO, DO NOT, VERIFY blocks
        blocks, matched_contact = generate_guidance_blocks(
            risk_assessment=risk_assessment,
            conversation_analysis=conversation_analysis,
            trusted_contacts=trusted_contacts
        )

        # Generate optional draft verification message
        contact_name = matched_contact.name if matched_contact else None
        draft_msg = generate_draft_verification_message(
            claimed_identity=claimed_identity,
            action_type=action_type,
            matched_contact_name=contact_name
        ) if risk_level != ProtectionLevel.SAFE.value else None

        return VerificationPlan(
            protection_level=protection_level,
            recommended_action=recommended_action,
            verification_method=blocks.verify,
            why=blocks.why,
            do=blocks.do,
            do_not=blocks.do_not,
            verify=blocks.verify,
            draft_verification_message=draft_msg,
            confidence=confidence,
            trusted_contact_used=matched_contact.to_dict() if matched_contact else None
        )

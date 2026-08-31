"""
Master TrustShield Protection Agent (Phase 4).
Translates risk engine assessments into safe, action-specific, identity-tailored user guidance.
Guarantees 100% deterministic fallback when offline or without LLM.
"""

from typing import Dict, Any, List, Optional
from ai.verification.verification_schema import VerificationPlan, TrustedContact
from ai.verification.verification_planner import VerificationPlanner


class ProtectionAgent:
    """TrustShield Protection Agent."""

    def __init__(self, use_llm_formatter: bool = False):
        """
        Args:
            use_llm_formatter: If True, attempts to polish output wording using LLM (if available).
                               Deterministic policy engine remains authoritative for all safety decisions.
        """
        self.planner = VerificationPlanner()
        self.use_llm_formatter = use_llm_formatter

    def generate_protection_guidance(
        self,
        risk_assessment: Dict[str, Any],
        conversation_analysis: Optional[Dict[str, Any]] = None,
        trusted_contacts: Optional[List[TrustedContact]] = None
    ) -> VerificationPlan:
        """Master method generating user protection guidance.

        Args:
            risk_assessment: Output dict from Phase 3 Risk Engine.
            conversation_analysis: Optional output dict from Phase 2 Conversation Intelligence.
            trusted_contacts: Optional user-provided trusted contacts.

        Returns:
            Validated VerificationPlan dataclass instance.
        """
        # 1. Deterministic Policy Plan (Always Authoritative)
        plan = self.planner.plan_verification(
            risk_assessment=risk_assessment,
            conversation_analysis=conversation_analysis,
            trusted_contacts=trusted_contacts
        )

        # 2. Optional LLM Polish (Strictly constrained: cannot alter protection_level or recommended_action)
        if self.use_llm_formatter:
            try:
                # LLM formatting hook placeholder for future API wiring
                pass
            except Exception:
                # Fall back gracefully to deterministic plan
                pass

        return plan

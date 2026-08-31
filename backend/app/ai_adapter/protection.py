import logging
from typing import Any, Dict, Optional

from app.ai_adapter import bootstrap_ai_root
from app.config import settings
from app.models import (
    ProtectionAgentError,
    ProtectionAgentFailedError,
    ProtectionAgentUnavailableError,
)

logger = logging.getLogger("trustshield-backend.ai_protection_adapter")


class AIProtectionAdapter:
    """
    Thin backend adapter wrapping the existing TrustShield Protection Agent
    located at D:\\TrustShield\\ai\\verification\\protection_agent.py.
    Translates risk assessments into human-centered safe intervention recommendations.
    Enforces strict safety invariants (recommendation != execution, user_confirmation_required: true).
    """

    def __init__(self):
        self._initialized = False
        self._agent_instance = None
        self._readiness_status = "UNAVAILABLE"

    def initialize(self) -> bool:
        """Initializes AI root path and loads the existing ProtectionAgent instance."""
        try:
            if not bootstrap_ai_root():
                self._readiness_status = "UNAVAILABLE"
                return False

            # Import existing AI ProtectionAgent implementation
            from ai.verification.protection_agent import ProtectionAgent

            self._agent_instance = ProtectionAgent(use_llm_formatter=False)

            self._initialized = True
            self._readiness_status = "READY"
            logger.info("AIProtectionAdapter initialized successfully with ProtectionAgent.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AIProtectionAdapter: {e}", exc_info=True)
            self._readiness_status = "ERROR"
            self._initialized = False
            return False

    def is_available(self) -> bool:
        """Returns True if the protection adapter is ready and initialized."""
        if not self._initialized:
            return self.initialize()
        return self._initialized

    def get_readiness_status(self) -> str:
        """Returns readiness status string ('READY', 'UNAVAILABLE', 'ERROR')."""
        if not self._initialized:
            self.initialize()
        return self._readiness_status

    def generate_guidance(
        self,
        risk_assessment: Dict[str, Any],
        conversation_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates user protection guidance and safe intervention recommendations from risk engine output.
        """
        if not self.is_available() or self._agent_instance is None:
            raise ProtectionAgentUnavailableError(
                "TrustShield AI Protection Agent service is unavailable. Check TRUSTSHIELD_AI_ROOT configuration."
            )

        try:
            plan = self._agent_instance.generate_protection_guidance(
                risk_assessment=risk_assessment,
                conversation_analysis=conversation_analysis
            )

            res_dict = plan.to_dict() if hasattr(plan, "to_dict") else dict(plan)
            res_dict["status"] = "available"
            
            # Enforce safety invariant: User confirmation required for non-SAFE actions
            prot_level = res_dict.get("protection_level", "SAFE")
            res_dict["user_confirmation_required"] = prot_level not in ("SAFE", "UNCERTAIN")

            # Extract evidence basis tags for transparency
            evidence_basis = []
            if conversation_analysis:
                act = conversation_analysis.get("requested_action", {}).get("type")
                if act and act != "no_risky_action":
                    evidence_basis.append(act)

                manip = conversation_analysis.get("manipulation", {})
                for tactic, score in manip.items():
                    if isinstance(score, (int, float)) and score >= 0.50:
                        evidence_basis.append(tactic)

                imp = conversation_analysis.get("impersonation", {}).get("claimed_identity")
                if imp and imp != "unknown":
                    evidence_basis.append(f"impersonation_{imp}")

            res_dict["evidence_basis"] = evidence_basis
            return res_dict

        except Exception as e:
            logger.error(f"Error during Protection Agent guidance generation: {e}", exc_info=True)
            raise ProtectionAgentFailedError(f"Protection Agent guidance generation failed: {str(e)}")


# Global adapter instance
default_protection_adapter = AIProtectionAdapter()

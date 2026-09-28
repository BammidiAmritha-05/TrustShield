from typing import Any, Dict


class ActionGateService:
    """
    Deterministic safety boundary between protection guidance
    and the user's next action.

    This service does not execute, block, or modify any external action.
    It only determines what TrustShield should allow, warn, pause,
    or hold for verification.
    """

    GATE_RULES = {
        "SAFE": {
            "decision": "ALLOW",
            "can_proceed": True,
            "requires_verification": False,
            "reason": "No high-risk action requires intervention."
        },
        "CAUTION": {
            "decision": "WARN",
            "can_proceed": True,
            "requires_verification": True,
            "reason": "Potential risk indicators were detected. Proceed only after reviewing the warning."
        },
        "SUSPICIOUS": {
            "decision": "PAUSE_AND_VERIFY",
            "can_proceed": False,
            "requires_verification": True,
            "reason": "Suspicious indicators were detected. Pause the requested action and verify independently."
        },
        "HIGH_RISK": {
            "decision": "BLOCK_AND_VERIFY",
            "can_proceed": False,
            "requires_verification": True,
            "reason": "High-risk indicators were detected. Do not proceed until the request is independently verified."
        },
        "UNCERTAIN": {
            "decision": "HOLD_FOR_VERIFICATION",
            "can_proceed": False,
            "requires_verification": True,
            "reason": "TrustShield cannot establish sufficient confidence. Hold the action and verify independently."
        },
    }

    def evaluate(
        self,
        risk_assessment: Dict[str, Any],
        protection_guidance: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate whether the user's next action should be allowed,
        warned, paused, or held for verification.
        """

        protection_level = protection_guidance.get(
            "protection_level",
            risk_assessment.get("risk_level", "UNCERTAIN")
        )

        protection_level = str(protection_level).upper()

        rule = self.GATE_RULES.get(
            protection_level,
            self.GATE_RULES["UNCERTAIN"]
        )

        return {
            "status": "available",
            "gate_decision": rule["decision"],
            "can_proceed": rule["can_proceed"],
            "requires_verification": rule["requires_verification"],
            "protection_level": protection_level,
            "recommended_action": protection_guidance.get(
                "recommended_action"
            ),
            "user_confirmation_required": protection_guidance.get(
                "user_confirmation_required",
                False
            ),
            "reason": rule["reason"],
        }


default_action_gate_service = ActionGateService()
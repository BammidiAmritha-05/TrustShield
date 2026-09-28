from typing import Any, Dict


class RecoveryService:
    """
    Deterministic post-risk recovery guidance.

    This service provides safe next steps after a potentially
    harmful interaction. It does not execute external recovery
    actions or claim that a loss has been reversed.
    """

    RECOVERY_RULES = {
        "share_otp": {
            "severity": "URGENT",
            "title": "Secure the affected account immediately",
            "steps": [
                "Stop sharing any further OTPs or verification codes.",
                "Contact the relevant bank or service through its official channel.",
                "Review recent account activity for unauthorized actions.",
                "Change affected security credentials if the official service recommends it.",
            ],
        },
        "share_password": {
            "severity": "URGENT",
            "title": "Secure the affected account",
            "steps": [
                "Stop communicating with the requester.",
                "Change the affected password using the official website or app.",
                "Sign out or revoke unfamiliar active sessions if the service supports it.",
                "Enable additional account security such as multi-factor authentication.",
            ],
        },
        "share_bank_details": {
            "severity": "URGENT",
            "title": "Protect your financial account",
            "steps": [
                "Do not provide any additional financial information.",
                "Contact your bank through an official channel.",
                "Monitor recent and upcoming account transactions.",
                "Follow the bank's instructions for securing the account.",
            ],
        },
        "transfer_money": {
            "severity": "URGENT",
            "title": "Act quickly on the financial transaction",
            "steps": [
                "Do not send any additional money.",
                "Contact your bank or payment provider immediately through an official channel.",
                "Provide the transaction details and request guidance on available protective or dispute procedures.",
                "Preserve transaction records and relevant communication as evidence.",
            ],
        },
        "approve_payment": {
            "severity": "URGENT",
            "title": "Stop further payment activity",
            "steps": [
                "Do not approve any additional payment request.",
                "Contact the bank or payment provider through its official channel.",
                "Review recent payment activity for unauthorized transactions.",
                "Preserve payment records and related communication.",
            ],
        },
        "install_remote_access": {
            "severity": "URGENT",
            "title": "Secure the device and accounts",
            "steps": [
                "Stop the remote session if it is still active.",
                "Disconnect the device from the network if you suspect active unauthorized access.",
                "Remove unauthorized remote-access software when safe to do so.",
                "Change important account credentials from a trusted device.",
                "Seek trusted technical assistance if you cannot verify that the device is secure.",
            ],
        },
        "click_link": {
            "severity": "HIGH",
            "title": "Stop interacting with the suspicious link",
            "steps": [
                "Do not open the link again or provide additional information.",
                "If credentials were entered, secure the affected account using its official website or app.",
                "Monitor the affected account for unusual activity.",
                "Preserve the suspicious message or link as evidence.",
            ],
        },
        "share_identity_document": {
            "severity": "HIGH",
            "title": "Protect the exposed identity information",
            "steps": [
                "Do not provide additional identity documents.",
                "Contact the relevant official organization through an independently verified channel.",
                "Monitor for suspicious account or identity activity.",
                "Preserve the original request and submitted information as evidence.",
            ],
        },
        "change_account_details": {
            "severity": "HIGH",
            "title": "Secure the account settings",
            "steps": [
                "Do not make further account changes based on the suspicious request.",
                "Access the service directly through its official website or app.",
                "Review recent account changes.",
                "Contact the service through an independently verified support channel if unauthorized changes occurred.",
            ],
        },
        "disclose_sensitive_information": {
            "severity": "HIGH",
            "title": "Protect the disclosed information",
            "steps": [
                "Stop providing additional sensitive information.",
                "Contact the relevant organization through an official channel.",
                "Review affected accounts or services for unusual activity.",
                "Preserve the conversation as evidence.",
            ],
        },
        "no_risky_action": {
            "severity": "NONE",
            "title": "No recovery action is currently required",
            "steps": [
                "Do not take further action based only on the suspicious request.",
                "Continue to verify unexpected requests independently.",
            ],
        },
    }

    def generate_recovery_guidance(
        self,
        risk_assessment: Dict[str, Any],
        protection_guidance: Dict[str, Any],
        action_gate: Dict[str, Any],
        conversation_analysis: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Generate deterministic recovery guidance based on the
        detected action and TrustShield safety assessment.
        """

        conversation_analysis = conversation_analysis or {}

        requested_action = conversation_analysis.get(
            "requested_action",
            {}
        )

        if isinstance(requested_action, dict):
            action_type = requested_action.get(
                "type",
                "no_risky_action",
            )
        else:
            action_type = str(requested_action)

        action_type = str(action_type).lower()

        rule = self.RECOVERY_RULES.get(
            action_type,
            self.RECOVERY_RULES["no_risky_action"],
        )

        protection_level = str(
            protection_guidance.get(
                "protection_level",
                risk_assessment.get("risk_level", "UNCERTAIN"),
            )
        ).upper()

        gate_decision = str(
            action_gate.get(
                "gate_decision",
                "HOLD_FOR_VERIFICATION",
            )
        )

        recovery_required = (
            rule["severity"] != "NONE"
            and protection_level != "SAFE"
        )

        return {
            "status": "available",
            "recovery_required": recovery_required,
            "severity": rule["severity"],
            "title": rule["title"],
            "action_type": action_type,
            "protection_level": protection_level,
            "gate_decision": gate_decision,
            "steps": rule["steps"],
            "external_action_taken": False,
            "loss_reversed": False,
            "evidence_preservation_recommended": recovery_required,
        }


default_recovery_service = RecoveryService()
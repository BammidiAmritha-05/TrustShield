"""
Draft Verification Message Generator for TrustShield AI (Phase 4).
Generates copyable, optional verification text messages for the user to inspect and send manually.
NEVER sends messages automatically.
"""

from typing import Dict, Any, Optional


def generate_draft_verification_message(
    claimed_identity: str,
    action_type: str,
    matched_contact_name: Optional[str] = None
) -> Optional[str]:
    """Generates a polite, copyable draft verification text message.

    Args:
        claimed_identity: Claimed entity identity (family_member, bank, executive, etc.).
        action_type: Requested action type (transfer_money, share_otp, etc.).
        matched_contact_name: Optional name of matched trusted contact.

    Returns:
        Copyable draft message string or None if no message needed.
    """
    if action_type == "no_risky_action":
        return None

    if claimed_identity == "family_member":
        recipient = matched_contact_name if matched_contact_name else "there"
        return f"Hi {recipient}, I received a message regarding an urgent request. Please call me back on my saved number when you see this to confirm."

    elif claimed_identity == "bank":
        return "I am pausing this request to verify through the bank's official mobile app / published customer helpline."

    elif claimed_identity == "executive":
        recipient = matched_contact_name if matched_contact_name else "team"
        return f"Hi {recipient}, I will confirm this payment request through our standard corporate portal before authorizing."

    elif claimed_identity in ["police", "government"]:
        return "I am taking note of this notice and will verify directly with the official department portal."

    elif claimed_identity == "customer_support":
        return "I will log into the official company website directly to manage my account inquiry."

    elif claimed_identity == "delivery_service":
        return "I am checking my delivery order status directly inside the official mobile app."

    else:
        return "I am pausing this transaction to confirm through an independent official channel before proceeding."

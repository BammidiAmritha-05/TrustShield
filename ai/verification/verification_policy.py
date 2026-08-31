"""
Action-Specific & Identity-Specific Safety Policies for TrustShield AI (Phase 4).
Deterministic policy rules for safe recommendations.
"""

from typing import Dict, Any, List, Optional, Tuple
from ai.verification.verification_schema import TrustedContact


# Action-Specific Safety Directives
ACTION_SAFETY_RULES: Dict[str, Dict[str, str]] = {
    "transfer_money": {
        "recommended_action": "PAUSE_TRANSFER",
        "do": "Pause the transfer immediately and verify the request through an independent channel.",
        "do_not": "Do NOT transfer money using payment links, UPI IDs, or bank details provided during this call.",
        "potential_harm": "Irreversible financial loss.",
    },
    "share_otp": {
        "recommended_action": "WITHHOLD_OTP",
        "do": "Keep the OTP private. If account verification is needed, log in directly through the official app.",
        "do_not": "Never read out or share any 4-digit or 6-digit OTP with anyone.",
        "potential_harm": "Account takeover and unauthorized transaction approval.",
    },
    "share_password": {
        "recommended_action": "WITHHOLD_PASSWORD",
        "do": "Refuse to share passwords. Change your password on the official portal if compromise is suspected.",
        "do_not": "Never type or state passwords on third-party links or during incoming calls.",
        "potential_harm": "Complete credential theft and identity compromise.",
    },
    "share_bank_details": {
        "recommended_action": "WITHHOLD_BANK_DETAILS",
        "do": "Disconnect and verify account requests through your financial institution's official branch or app.",
        "do_not": "Do NOT disclose bank account numbers, CVVs, or card expiry dates over the phone.",
        "potential_harm": "Unauthorized debit and financial fraud.",
    },
    "approve_payment": {
        "recommended_action": "PAUSE_APPROVAL",
        "do": "Confirm payment authorization via established internal or personal verification channels.",
        "do_not": "Do NOT tap approve or enter UPI PIN for unexpected collect requests.",
        "potential_harm": "Direct debit from bank account.",
    },
    "install_remote_access": {
        "recommended_action": "DENY_REMOTE_ACCESS",
        "do": "Disconnect the call and uninstall any recently downloaded remote support tools.",
        "do_not": "Do NOT download AnyDesk, TeamViewer, or share your screen with unverified callers.",
        "potential_harm": "Full remote control of your device and data theft.",
    },
    "click_link": {
        "recommended_action": "DO_NOT_CLICK_LINK",
        "do": "Open your web browser and manually navigate to the official website or app.",
        "do_not": "Do NOT tap links sent via SMS or messaging apps from unverified callers.",
        "potential_harm": "Phishing and malicious APK malware installation.",
    },
    "share_identity_document": {
        "recommended_action": "WITHHOLD_DOCUMENTS",
        "do": "Verify the requesting authority independently before transmitting identity documents.",
        "do_not": "Do NOT send photos of Aadhaar, PAN card, or passport over messaging platforms.",
        "potential_harm": "Synthetic identity fraud and loan impersonation.",
    },
    "change_account_details": {
        "recommended_action": "VERIFY_ACCOUNT_CHANGE",
        "do": "Confirm account modification requests via known internal company or official support channels.",
        "do_not": "Do NOT update recipient bank accounts or email addresses based on unverified instructions.",
        "potential_harm": "Business email compromise and misdirected funds.",
    },
    "disclose_sensitive_information": {
        "recommended_action": "WITHHOLD_INFORMATION",
        "do": "Withhold sensitive personal details until caller identity and purpose are confirmed.",
        "do_not": "Do NOT share personal or financial information during unsolicited calls.",
        "potential_harm": "Targeted social engineering and profiling.",
    },
    "no_risky_action": {
        "recommended_action": "STAY_AWARE",
        "do": "Continue normal conversation while remaining aware of unsolicited requests.",
        "do_not": "No risky action requested; no immediate restriction required.",
        "potential_harm": "None detected.",
    },
}


# Identity-Specific Verification Strategies
IDENTITY_VERIFICATION_RULES: Dict[str, str] = {
    "family_member": "Contact your family member directly using your existing saved phone number or trusted family contact channel.",
    "bank": "Log into your official banking app or call the published customer service number printed on the back of your debit/credit card.",
    "executive": "Confirm this instruction using your official corporate directory extension or internal messaging system.",
    "police": "Do NOT use phone numbers supplied by the caller. Contact your local police station or official government portal independently.",
    "government": "Verify the notice by searching the official government department portal independently.",
    "customer_support": "Open the official company app or website directly and contact support via their verified help desk.",
    "delivery_service": "Check your parcel tracking status directly inside the official courier app or official order history page.",
    "unknown": "Verify the caller's identity through an independent, official channel before taking any action.",
}


def get_identity_verification_guidance(
    claimed_identity: str,
    trusted_contacts: Optional[List[TrustedContact]] = None
) -> Tuple[str, Optional[TrustedContact]]:
    """Returns identity-tailored verification instructions and checks for matching trusted contacts.

    Args:
        claimed_identity: Claimed entity identity (e.g. family_member, bank, executive).
        trusted_contacts: Optional list of user-provided trusted contacts.

    Returns:
        Tuple of (verification_instruction_string, matched_trusted_contact_or_None).
    """
    matched_contact: Optional[TrustedContact] = None

    if trusted_contacts:
        for contact in trusted_contacts:
            if contact.relationship.lower() in claimed_identity.lower() or claimed_identity.lower() in contact.relationship.lower():
                matched_contact = contact
                break

    if matched_contact:
        guidance = f"Contact {matched_contact.name} ({matched_contact.relationship}) via their saved channel: {matched_contact.verification_channel}."
        return guidance, matched_contact

    guidance = IDENTITY_VERIFICATION_RULES.get(claimed_identity, IDENTITY_VERIFICATION_RULES["unknown"])
    return guidance, None

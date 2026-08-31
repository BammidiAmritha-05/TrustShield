"""
Action Detection Module for TrustShield Conversation Intelligence.
Identifies the exact requested action and sensitivity level.
"""

import re
from typing import Optional, Dict, Any
from ai.intelligence.schemas import ActionResult, RequestedActionType, ActionSensitivity


def detect_requested_action(text: str, session_context: Optional[Dict[str, Any]] = None) -> ActionResult:
    """Extracts the specific action requested of the user and maps its sensitivity.

    Args:
        text: Conversation text snippet.
        session_context: Optional session context dictionary.

    Returns:
        ActionResult containing requested action type, sensitivity, and confidence.
    """
    text_lower = text.lower()
    # Normalize comma-formatted numbers e.g. 1,00,000 -> 100000 for robust regex matching
    text_norm = re.sub(r"(\d+),(\d+)", r"\1\2", text_lower)

    # Contextual False-Positive Exception Checks:
    # Example: "Send the OTP from your own phone to your own device" or "Do not give OTP to anyone"
    if ("own device" in text_norm or "own phone" in text_norm or "do not share" in text_norm or "never share" in text_norm) and ("otp" in text_norm or "password" in text_norm):
        return ActionResult(
            type=RequestedActionType.NO_RISKY_ACTION.value,
            sensitivity=ActionSensitivity.NONE.value,
            confidence=0.95,
            details="Instruction to retain credential on user's own device / advisory against sharing."
        )

    # 1. Install Remote Access Tools
    if any(k in text_norm for k in ["anydesk", "teamviewer", "rustdesk", "quicksupport", "install remote", "screen share", "download remote", "share screen"]):
        return ActionResult(
            type=RequestedActionType.INSTALL_REMOTE_ACCESS.value,
            sensitivity=ActionSensitivity.CRITICAL.value,
            confidence=0.98
        )

    # 2. Share OTP / Verification Code
    if any(k in text_norm for k in ["share otp", "send otp", "tell me the otp", "tell me your otp", "your otp", "the otp", "enter otp", "provide otp", "code sent", "read the code", "read me the", "give me the otp", "otp is", "read out", "share verification code"]):
        return ActionResult(
            type=RequestedActionType.SHARE_OTP.value,
            sensitivity=ActionSensitivity.CRITICAL.value,
            confidence=0.98
        )

    # 3. Share Password / PIN
    if any(k in text_norm for k in ["share password", "tell me your pin", "upi pin", "bank password", "enter pin", "provide your password"]):
        return ActionResult(
            type=RequestedActionType.SHARE_PASSWORD.value,
            sensitivity=ActionSensitivity.CRITICAL.value,
            confidence=0.97
        )

    # 4. Transfer Money / Payment Demands / Wire Transfer (including paraphrases, Indian comma numbers, dollars)
    money_patterns = [
        r"send\s+(?:rs\.?|₹|\$)?\s*\d+",
        r"transfer\s+(?:rs\.?|₹|\$)?\s*\d+",
        r"pay\s+(?:rs\.?|₹|\$)?\s*\d+",
        r"need\s+(?:rs\.?|₹|\$)?\s*\d+",
        r"process\s+(?:rs\.?|₹|\$)?\s*\d+",
        r"\d+\s*(?:dollars|rupees|₹|\$|k|lakh|crore)",
        r"(?:eighty|fifty|ten|twenty|hundred|thousand|lakh|crore)",
        r"transfer\s+money",
        r"wire\s+transfer",
        r"execute\s+.*transfer",
        r"process\s+.*payment",
        r"authorize\s+.*payment",
        r"make\s+the\s+payment",
        r"send\s+money",
        r"pay\s+rupees",
        r"gpay",
        r"phonepe",
        r"upi\s+transfer"
    ]
    if any(re.search(pat, text_norm) for pat in money_patterns) or ("send" in text_norm and any(k in text_norm for k in ["rupees", "₹", "rs", "amount", "money", "dollars", "$", "payment", "cab fare"])) or ("transfer" in text_norm and any(k in text_norm for k in ["wire", "account", "fund", "money", "thousand", "payment", "rupees", "clearance"])) or ("pay" in text_norm and any(k in text_norm for k in ["fee", "penalty", "customs", "tax", "charge"])):
        return ActionResult(
            type=RequestedActionType.TRANSFER_MONEY.value,
            sensitivity=ActionSensitivity.CRITICAL.value,
            confidence=0.96
        )

    # 5. Share Bank Details
    if any(k in text_norm for k in ["account number", "ifsc code", "card number", "cvv", "expiry date", "bank account details"]):
        return ActionResult(
            type=RequestedActionType.SHARE_BANK_DETAILS.value,
            sensitivity=ActionSensitivity.HIGH.value,
            confidence=0.92
        )

    # 6. Click Link
    if any(k in text_norm for k in ["click link", "open this link", "visit link", "http", "https", "bit.ly"]):
        return ActionResult(
            type=RequestedActionType.CLICK_LINK.value,
            sensitivity=ActionSensitivity.MEDIUM.value,
            confidence=0.89
        )

    # 7. Share Identity Document
    if any(k in text_norm for k in ["aadhaar card", "pan card", "passport copy", "driving license", "photo of id", "photo of your aadhaar"]):
        return ActionResult(
            type=RequestedActionType.SHARE_IDENTITY_DOCUMENT.value,
            sensitivity=ActionSensitivity.MEDIUM.value,
            confidence=0.87
        )

    # 8. No Risky Action / General Interaction
    return ActionResult(
        type=RequestedActionType.NO_RISKY_ACTION.value,
        sensitivity=ActionSensitivity.NONE.value,
        confidence=0.90
    )

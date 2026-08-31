"""
Intent Detection Module for TrustShield Conversation Intelligence.
Categorizes interaction intent without applying scam/fraud labels directly.
"""

import re
from typing import Optional, Dict, Any
from ai.intelligence.schemas import IntentResult, IntentCategory


def detect_intent(text: str, session_context: Optional[Dict[str, Any]] = None) -> IntentResult:
    """Detects the primary intent of the conversation.

    Args:
        text: Conversation text / transcript snippet.
        session_context: Optional session context dictionary.

    Returns:
        IntentResult object containing intent type and confidence.
    """
    text_lower = text.lower()

    # Contextual False-Positive Exception
    if "own device" in text_lower or "own phone" in text_lower:
        return IntentResult(type=IntentCategory.INFORMATION_REQUEST.value, confidence=0.85)

    # 1. Financial Fraud / Scam Patterns
    if any(k in text_lower for k in [
        "digital arrest", "police case registered", "cbi investigation", "warrant issued",
        "customs seized", "illegal package", "account blocked transfer immediately", "send money to safe account",
        "confidential acquisition", "urgent wire transfer", "customs penalty"
    ]):
        return IntentResult(type=IntentCategory.FINANCIAL_FRAUD.value, confidence=0.92)

    # 2. Remote Access
    if any(k in text_lower for k in [
        "anydesk", "teamviewer", "rustdesk", "quicksupport", "install remote", "screen sharing", "allow access"
    ]):
        return IntentResult(type=IntentCategory.REMOTE_ACCESS.value, confidence=0.95)

    # 3. Credential Theft / OTP Sharing
    if any(k in text_lower for k in ["otp", "one time password", "verification code", "password", "pin number", "cvv"]):
        if any(k in text_lower for k in ["share", "send", "tell me", "read out", "give me", "provide", "read out the"]):
            return IntentResult(type=IntentCategory.CREDENTIAL_THEFT.value, confidence=0.94)

    # 4. Payment Request / Financial Transfer
    if any(k in text_lower for k in [
        "send money", "transfer money", "transfer ₹", "send ₹", "pay rupees", "gpay me", "upi transfer", "borrow money", "need ₹", "send ₹500"
    ]) or re.search(r"send\s+(?:rs\.?|₹|\$)?\s*\d+", text_lower):
        if any(k in text_lower for k in ["emergency", "hospital", "bail", "accident", "stuck", "immediately"]):
            return IntentResult(type=IntentCategory.FINANCIAL_FRAUD.value, confidence=0.88)
        return IntentResult(type=IntentCategory.PAYMENT_REQUEST.value, confidence=0.85)

    # 5. Account Access / Recovery
    if any(k in text_lower for k in ["lockout", "account frozen", "unfreeze account", "kyc update", "bank account update"]):
        return IntentResult(type=IntentCategory.ACCOUNT_ACCESS.value, confidence=0.86)

    # 6. Identity Verification
    if any(k in text_lower for k in ["verify your identity", "aadhaar", "pan card", "id proof", "passport copy"]):
        return IntentResult(type=IntentCategory.IDENTITY_VERIFICATION.value, confidence=0.82)

    # 7. General Information Request
    if any(k in text_lower for k in ["what is your", "can you tell me", "where do you", "send address", "email id"]):
        return IntentResult(type=IntentCategory.INFORMATION_REQUEST.value, confidence=0.75)

    # 8. Harmless Casual Conversation
    if any(k in text_lower for k in ["hello", "hi", "how are you", "dinner", "lunch", "good morning", "see you", "thanks"]):
        return IntentResult(type=IntentCategory.HARMLESS_CONVERSATION.value, confidence=0.90)

    return IntentResult(type=IntentCategory.OTHER.value, confidence=0.50)

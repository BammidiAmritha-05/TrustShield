"""
Impersonation Detection Module for TrustShield Conversation Intelligence.
Extracts claimed identity and evaluates potential impersonation claims.
"""

from typing import Optional, Dict, Any
from ai.intelligence.schemas import ImpersonationResult, ClaimedIdentityCategory


def detect_impersonation_claim(text: str, session_context: Optional[Dict[str, Any]] = None) -> ImpersonationResult:
    """Detects the claimed identity in the conversation text.

    Args:
        text: Conversation text snippet.
        session_context: Optional session context dictionary.

    Returns:
        ImpersonationResult containing claimed identity category, possible impersonation flag, and confidence.
    """
    text_lower = text.lower()

    # Session context override if caller specified claimed role
    if session_context and "claimed_role" in session_context:
        role = session_context["claimed_role"].lower()
        verified = session_context.get("identity_verified", False)
        return ImpersonationResult(
            claimed_identity=role,
            possible_impersonation=not verified,
            confidence=0.90
        )

    # 1. Family Member Claim
    if any(k in text_lower for k in ["your son", "your daughter", "mom", "dad", "uncle", "cousin", "brother", "sister", "your nephew"]):
        return ImpersonationResult(
            claimed_identity=ClaimedIdentityCategory.FAMILY_MEMBER.value,
            possible_impersonation=True,
            confidence=0.88
        )

    # 2. Police / Law Enforcement
    if any(k in text_lower for k in ["police", "inspector", "cbi officer", "cyber crime department", "sub-inspector", "constable"]):
        return ImpersonationResult(
            claimed_identity=ClaimedIdentityCategory.POLICE.value,
            possible_impersonation=True,
            confidence=0.94
        )

    # 3. Bank Official
    if any(k in text_lower for k in ["bank manager", "sbi official", "hdfc support", "bank fraud department", "rbi representative", "card manager"]):
        return ImpersonationResult(
            claimed_identity=ClaimedIdentityCategory.BANK.value,
            possible_impersonation=True,
            confidence=0.92
        )

    # 4. Executive / CEO
    if any(k in text_lower for k in ["company ceo", "managing director", "boss", "chief executive", "president of company"]):
        return ImpersonationResult(
            claimed_identity=ClaimedIdentityCategory.EXECUTIVE.value,
            possible_impersonation=True,
            confidence=0.90
        )

    # 5. Government Official
    if any(k in text_lower for k in ["income tax department", "customs officer", "telecom authority", "trai official"]):
        return ImpersonationResult(
            claimed_identity=ClaimedIdentityCategory.GOVERNMENT.value,
            possible_impersonation=True,
            confidence=0.91
        )

    # 6. Customer Support
    if any(k in text_lower for k in ["customer care", "helpdesk", "tech support", "service agent", "support team"]):
        return ImpersonationResult(
            claimed_identity=ClaimedIdentityCategory.CUSTOMER_SUPPORT.value,
            possible_impersonation=True,
            confidence=0.85
        )

    # 7. Delivery / Courier
    if any(k in text_lower for k in ["fedex agent", "dhl courier", "delivery driver", "parcel officer"]):
        return ImpersonationResult(
            claimed_identity=ClaimedIdentityCategory.DELIVERY_SERVICE.value,
            possible_impersonation=True,
            confidence=0.86
        )

    return ImpersonationResult(
        claimed_identity=ClaimedIdentityCategory.UNKNOWN.value,
        possible_impersonation=False,
        confidence=0.50
    )

"""
Context Analyzer Module for TrustShield Conversation Intelligence.
Constructs contextual interaction state.
"""

from typing import Optional, Dict, Any
from ai.intelligence.schemas import ContextResult, ActionResult, ImpersonationResult, ManipulationResult


def analyze_context(
    text: str,
    action: ActionResult,
    impersonation: ImpersonationResult,
    manipulation: ManipulationResult,
    session_context: Optional[Dict[str, Any]] = None
) -> ContextResult:
    """Builds a ContextResult tracking identity verification, unusual requests, and verification availability.

    Args:
        text: Conversation text snippet.
        action: Extracted requested action result.
        impersonation: Extracted impersonation claim result.
        manipulation: Extracted manipulation tactics.
        session_context: Optional session context dictionary provided by caller.

    Returns:
        ContextResult object.
    """
    ctx = ContextResult()

    # Session context defaults
    if session_context:
        ctx.identity_verified = session_context.get("identity_verified", False)
        ctx.independent_verification_available = session_context.get("independent_verification_available", True)
        if "session_flags" in session_context:
            ctx.session_flags = session_context["session_flags"]

    # Evaluate if request is unusual based on context
    is_risky_action = action.sensitivity in ["critical", "high"]
    is_unverified_caller = not ctx.identity_verified
    is_high_pressure = manipulation.urgency > 0.7 or manipulation.secrecy > 0.7 or manipulation.fear > 0.7

    if is_risky_action and (is_unverified_caller or is_high_pressure):
        ctx.unusual_request = True
    else:
        ctx.unusual_request = False

    return ctx

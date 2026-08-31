"""
Master Conversation Intelligence Engine for TrustShield AI (Phase 2).
Orchestrates intent detection, requested action detection, manipulation scoring,
impersonation claim detection, context analysis, and plain-language explanation generation.
"""

from typing import Optional, Dict, Any
from ai.intelligence.schemas import ConversationAnalysisResult
from ai.intelligence.intent_detector import detect_intent
from ai.intelligence.action_detector import detect_requested_action
from ai.intelligence.manipulation_detector import detect_manipulation
from ai.intelligence.impersonation_detector import detect_impersonation_claim
from ai.intelligence.context_analyzer import analyze_context


def generate_explanation(
    intent: Any,
    action: Any,
    manipulation: Any,
    impersonation: Any,
    context: Any
) -> str:
    """Generates a plain-language explanation strictly derived from structured signals."""
    parts = []

    # 1. Action & Intent Description
    if action.type != "no_risky_action":
        action_formatted = action.type.replace('_', ' ')
        parts.append(f"a request to {action_formatted}")
    elif intent.type not in ["harmless_conversation", "other"]:
        intent_formatted = intent.type.replace('_', ' ')
        parts.append(f"an interaction involving {intent_formatted}")

    # 2. Manipulation Tactics Description
    tactics = []
    if manipulation.urgency >= 0.7:
        tactics.append("high urgency")
    if manipulation.secrecy >= 0.7:
        tactics.append("secrecy")
    if manipulation.fear >= 0.7:
        tactics.append("fear or threat of penalty")
    if manipulation.authority_pressure >= 0.7:
        tactics.append("authority pressure")

    if tactics:
        if parts:
            parts.append(f"combined with {', '.join(tactics)}")
        else:
            parts.append(f"high pressure tactics ({', '.join(tactics)})")

    # 3. Impersonation & Verification Context
    if impersonation.claimed_identity != "unknown":
        identity_str = f"a claimed identity of {impersonation.claimed_identity.replace('_', ' ')}"
        if not context.identity_verified:
            identity_str += " (unverified)"
        parts.append(f"from {identity_str}")

    if not parts:
        return "Standard conversation with no detected risky actions or manipulation tactics."

    explanation = "The interaction involves " + " ".join(parts) + "."
    return explanation.replace("  ", " ").strip()


def analyze_conversation(
    text: str,
    session_context: Optional[Dict[str, Any]] = None
) -> ConversationAnalysisResult:
    """Analyzes a conversation text snippet and returns a consolidated ConversationAnalysisResult.

    Args:
        text: Conversation text / transcript snippet.
        session_context: Optional session context dictionary.

    Returns:
        Validated ConversationAnalysisResult dataclass instance.
    """
    intent_res = detect_intent(text, session_context=session_context)
    action_res = detect_requested_action(text, session_context=session_context)
    manipulation_res = detect_manipulation(text, session_context=session_context)
    impersonation_res = detect_impersonation_claim(text, session_context=session_context)
    context_res = analyze_context(text, action_res, impersonation_res, manipulation_res, session_context=session_context)

    explanation = generate_explanation(intent_res, action_res, manipulation_res, impersonation_res, context_res)

    return ConversationAnalysisResult(
        intent=intent_res,
        requested_action=action_res,
        manipulation=manipulation_res,
        impersonation=impersonation_res,
        context=context_res,
        explanation=explanation
    )

"""
Manipulation Detection Module for TrustShield Conversation Intelligence.
Extracts social engineering and psychological pressure tactics.
"""

from typing import Optional, Dict, Any
from ai.intelligence.schemas import ManipulationResult


def detect_manipulation(text: str, session_context: Optional[Dict[str, Any]] = None) -> ManipulationResult:
    """Analyzes text for social engineering pressure tactics.

    Args:
        text: Conversation text snippet.
        session_context: Optional session context dictionary.

    Returns:
        ManipulationResult object with float scores (0.0 to 1.0) per tactic.
    """
    text_lower = text.lower()
    res = ManipulationResult()

    # 1. Urgency
    if any(k in text_lower for k in ["immediately", "immediate", "right now", "right away", "urgently", "within 5 minutes", "urgent", "hurry", "quick", "asap", "before it is too late", "time running out"]):
        res.urgency = 0.96
    elif any(k in text_lower for k in ["today", "soon", "need this"]):
        res.urgency = 0.60

    # 2. Secrecy
    if any(k in text_lower for k in ["don't tell anyone", "do not tell anyone", "do not disclose", "keep this secret", "confidential", "between you and me", "nobody else must know", "stay quiet", "keep it quiet", "do not discuss", "keep it between us", "do not contact anyone"]):
        res.secrecy = 0.91

    # 3. Fear
    if any(k in text_lower for k in ["arrest", "police", "jail", "legal action", "warrant", "frozen", "suspend", "penalty", "court", "investigation"]):
        res.fear = 0.90
    elif any(k in text_lower for k in ["problem", "issue", "warning"]):
        res.fear = 0.50

    # 4. Authority Pressure
    if any(k in text_lower for k in ["cbi", "police officer", "supreme court", "reserve bank", "rbi official", "senior manager", "ceo", "government official", "customs department"]):
        res.authority_pressure = 0.88

    # 5. Emotional Pressure
    if any(k in text_lower for k in ["hospital", "accident", "emergency", "please help", "life or death", "dying"]):
        res.emotional_pressure = 0.90

    # 6. Threat
    if any(k in text_lower for k in ["will arrest", "will block", "disconnect service", "send force", "file fir"]):
        res.threat = 0.85

    # 7. Reward / Financial Bait
    if any(k in text_lower for k in ["you won", "lottery", "cashback", "prize", "gift card", "exclusive reward"]):
        res.reward = 0.88

    # 8. Isolation
    if any(k in text_lower for k in ["do not end call", "stay on line", "do not consult anyone", "close the door"]):
        res.isolation = 0.85

    # 9. Intimidation
    if any(k in text_lower for k in ["strictly mandatory", "comply immediately", "severe consequences", "do not question"]):
        res.intimidation = 0.82

    # 10. Forced Compliance
    if any(k in text_lower for k in ["you must", "obligated to", "failure to comply"]):
        res.forced_compliance = 0.80

    return res

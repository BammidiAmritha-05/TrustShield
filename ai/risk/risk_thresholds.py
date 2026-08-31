"""
Scoring Weights, Thresholds, and Policy Bands for TrustShield Risk Engine (Phase 3).
Configurable parameters separate from scoring logic.
"""

from typing import Dict, Any
from enum import Enum


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"
    UNCERTAIN = "UNCERTAIN"


# Risk Band Boundaries (0 to 100)
RISK_BAND_THRESHOLDS = {
    RiskLevel.SAFE.value: (0, 29),
    RiskLevel.CAUTION.value: (30, 59),
    RiskLevel.SUSPICIOUS.value: (60, 79),
    RiskLevel.HIGH_RISK.value: (80, 100),
}


# Action Sensitivity Multipliers (0.0 to 1.0)
ACTION_SENSITIVITY_WEIGHTS: Dict[str, float] = {
    "critical": 40.0,
    "high": 25.0,
    "medium": 15.0,
    "low": 5.0,
    "none": 0.0,
}


# Manipulation Tactics Base Points (0.0 to 1.0 score scaled)
MANIPULATION_TACTIC_WEIGHTS: Dict[str, float] = {
    "urgency": 18.0,
    "secrecy": 18.0,
    "fear": 20.0,
    "authority_pressure": 15.0,
    "threat": 18.0,
    "isolation": 15.0,
    "emotional_pressure": 12.0,
    "reward": 10.0,
    "intimidation": 12.0,
    "forced_compliance": 10.0,
}


# Impersonation Base Weight
IMPERSONATION_BASE_WEIGHT: float = 15.0


# Voice Authenticity Max Contribution Weight (synthetic score * 35.0)
VOICE_AUTHENTICITY_MAX_WEIGHT: float = 35.0


def map_score_to_risk_level(score: float, confidence: float) -> str:
    """Maps a numerical score (0 to 100) to a TrustShield Policy Risk Level."""
    if confidence < 0.35:
        return RiskLevel.UNCERTAIN.value

    score = max(0.0, min(100.0, score))
    if score >= 80.0:
        return RiskLevel.HIGH_RISK.value
    elif score >= 60.0:
        return RiskLevel.SUSPICIOUS.value
    elif score >= 30.0:
        return RiskLevel.CAUTION.value
    else:
        return RiskLevel.SAFE.value

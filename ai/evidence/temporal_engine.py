"""
Temporal Evidence Accumulation Engine for TrustShield AI (Phase 3).
Accumulates evidence over interaction turns (T1, T2, T3...) using weighted decay, EMA, and hysteresis.
"""

from typing import List, Dict, Any, Optional
from ai.evidence.evidence_schema import NormalizedEvidence


class TemporalEngine:
    """Accumulates risk signals over time to reflect evolving call progression."""

    def __init__(self, alpha: float = 0.4, decay_factor: float = 0.90, cooldown_rate: float = 0.05):
        """
        Args:
            alpha: Exponential moving average smoothing factor (0.0 to 1.0).
            decay_factor: Weight decay for past evidence turns.
            cooldown_rate: Rate at which risk de-escalates if no new risk signals occur.
        """
        self.alpha = alpha
        self.decay_factor = decay_factor
        self.cooldown_rate = cooldown_rate
        self.temporal_risk_score: float = 0.0
        self.peak_risk_score: float = 0.0
        self.turn_history: List[Dict[str, Any]] = []

    def update(self, instantaneous_risk: float, turn_index: int, evidence_count: int) -> float:
        """Updates the temporal risk score with new turn evidence.

        Args:
            instantaneous_risk: The current turn's raw calculated risk score (0.0 to 100.0).
            turn_index: The current interaction turn index.
            evidence_count: Number of active evidence items in current turn.

        Returns:
            Updated temporal risk score (0.0 to 100.0).
        """
        if turn_index == 1:
            self.temporal_risk_score = instantaneous_risk
        else:
            if instantaneous_risk >= self.temporal_risk_score:
                # Accumulate/escalate score with EMA
                self.temporal_risk_score = (self.alpha * instantaneous_risk) + ((1 - self.alpha) * self.temporal_risk_score)
            else:
                # De-escalate with hysteresis/cooldown (decay slowly rather than dropping sharply)
                cooldown_delta = (self.temporal_risk_score - instantaneous_risk) * self.cooldown_rate
                self.temporal_risk_score = max(0.0, self.temporal_risk_score - cooldown_delta)

        # Track peak risk achieved
        if self.temporal_risk_score > self.peak_risk_score:
            self.peak_risk_score = self.temporal_risk_score

        # Update or record turn history
        turn_entry = {
            "turn_index": turn_index,
            "turn_number": turn_index,
            "instantaneous_risk": round(instantaneous_risk, 2),
            "temporal_risk": round(self.temporal_risk_score, 2),
            "risk_index": int(round(self.temporal_risk_score)),
            "evidence_count": evidence_count,
        }

        # If turn_history already has an entry for this turn_index, update in place; otherwise append
        if self.turn_history and self.turn_history[-1].get("turn_index") == turn_index:
            self.turn_history[-1].update(turn_entry)
        else:
            self.turn_history.append(turn_entry)

        return round(self.temporal_risk_score, 2)

    def get_timeline(self) -> List[Dict[str, Any]]:
        """Returns the full turn-by-turn risk timeline."""
        return self.turn_history

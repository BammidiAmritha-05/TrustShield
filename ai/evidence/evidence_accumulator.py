"""
Evidence Accumulator for TrustShield AI (Phase 3).
Normalizes and aggregates evidence streams from voice models, conversation intelligence, and context.
"""

from typing import List, Dict, Any, Optional
from ai.evidence.evidence_schema import NormalizedEvidence, EvidenceSource


class EvidenceAccumulator:
    """Accumulates and normalizes incoming evidence items across interaction turns."""

    def __init__(self):
        self.evidence_history: List[NormalizedEvidence] = []
        self.current_turn: int = 1

    def add_evidence(self, item: NormalizedEvidence) -> None:
        """Adds a normalized evidence item to history."""
        self.evidence_history.append(item)

    def advance_turn(self) -> None:
        """Increments the turn counter."""
        self.current_turn += 1

    def ingest_voice_result(self, voice_res: Dict[str, Any], turn_index: Optional[int] = None) -> List[NormalizedEvidence]:
        """Converts an analyze_audio output dict into normalized evidence items."""
        turn = turn_index if turn_index is not None else self.current_turn
        ev_items = []

        status = voice_res.get("status")
        if status == "available":
            synth_score = voice_res.get("synthetic_score", 0.0)
            bona_score = voice_res.get("bona_fide_score", 0.0)
            quality = voice_res.get("quality", "acceptable")
            reliability = 0.85 if quality == "good" else 0.65

            item = NormalizedEvidence(
                signal="synthetic_voice_probability",
                value=synth_score,
                confidence=0.80,
                source=EvidenceSource.VOICE_MODEL.value,
                reliability=reliability,
                turn_index=turn
            )
            self.add_evidence(item)
            ev_items.append(item)
        elif status == "insufficient_evidence":
            item = NormalizedEvidence(
                signal="voice_quality_unusable",
                value=voice_res.get("reason", "insufficient_evidence"),
                confidence=0.95,
                source=EvidenceSource.VOICE_MODEL.value,
                reliability=0.30,
                turn_index=turn
            )
            self.add_evidence(item)
            ev_items.append(item)

        return ev_items

    def ingest_conversation_result(self, conv_res: Dict[str, Any], turn_index: Optional[int] = None) -> List[NormalizedEvidence]:
        """Converts a ConversationAnalysisResult dict into normalized evidence items."""
        turn = turn_index if turn_index is not None else self.current_turn
        ev_items = []

        # 1. Intent Evidence
        intent = conv_res.get("intent", {})
        if intent.get("type"):
            item = NormalizedEvidence(
                signal="intent_category",
                value=intent["type"],
                confidence=intent.get("confidence", 0.80),
                source=EvidenceSource.INTENT.value,
                turn_index=turn
            )
            self.add_evidence(item)
            ev_items.append(item)

        # 2. Requested Action Evidence
        action = conv_res.get("requested_action", {})
        if action.get("type") and action["type"] != "no_risky_action":
            item = NormalizedEvidence(
                signal="requested_action",
                value=action["type"],
                confidence=action.get("confidence", 0.90),
                source=EvidenceSource.ACTION.value,
                turn_index=turn
            )
            self.add_evidence(item)
            ev_items.append(item)

        # 3. Manipulation Tactics Evidence
        manip = conv_res.get("manipulation", {})
        for tactic, score in manip.items():
            if isinstance(score, (int, float)) and score >= 0.50:
                item = NormalizedEvidence(
                    signal=f"manipulation_{tactic}",
                    value=score,
                    confidence=0.85,
                    source=EvidenceSource.MANIPULATION.value,
                    turn_index=turn
                )
                self.add_evidence(item)
                ev_items.append(item)

        # 4. Impersonation Claim Evidence
        imp = conv_res.get("impersonation", {})
        if imp.get("claimed_identity") and imp["claimed_identity"] != "unknown":
            item = NormalizedEvidence(
                signal="claimed_identity",
                value=imp["claimed_identity"],
                confidence=imp.get("confidence", 0.85),
                source=EvidenceSource.IMPERSONATION.value,
                turn_index=turn
            )
            self.add_evidence(item)
            ev_items.append(item)

        # 5. Context Evidence
        ctx = conv_res.get("context", {})
        if "identity_verified" in ctx:
            item = NormalizedEvidence(
                signal="identity_verified",
                value=ctx["identity_verified"],
                confidence=0.95,
                source=EvidenceSource.CONTEXT.value,
                turn_index=turn
            )
            self.add_evidence(item)
            ev_items.append(item)

        return ev_items

    def get_latest_evidence(self) -> List[NormalizedEvidence]:
        """Returns all evidence accumulated so far."""
        return self.evidence_history

import logging
from typing import Dict, Any, Optional

from app.ai_adapter import bootstrap_ai_root

logger = logging.getLogger("trustshield-backend.evidence_store")

MAX_EVIDENCE_RECORDS_PER_SESSION = 50


class SessionEvidenceStore:
    """
    In-memory session-scoped evidence manager.
    Isolates RiskEngine and EvidenceAccumulator instances per session with bounded memory limits.
    """

    def __init__(self):
        self._session_engines: Dict[str, Any] = {}
        self._session_turn_counts: Dict[str, int] = {}

    def get_or_create_engine(self, session_id: str) -> Any:
        """Retrieves or instantiates a RiskEngine for the specified session_id."""
        if session_id not in self._session_engines:
            if not bootstrap_ai_root():
                raise RuntimeError("Failed to bootstrap TRUSTSHIELD_AI_ROOT for RiskEngine instantiation.")

            from ai.risk.risk_engine import RiskEngine

            self._session_engines[session_id] = RiskEngine()
            self._session_turn_counts[session_id] = 1

        engine = self._session_engines[session_id]

        # Enforce bounded memory limit on evidence history
        if hasattr(engine, "accumulator") and hasattr(engine.accumulator, "evidence_history"):
            history = engine.accumulator.evidence_history
            if len(history) > MAX_EVIDENCE_RECORDS_PER_SESSION:
                # Keep latest MAX_EVIDENCE_RECORDS_PER_SESSION items
                engine.accumulator.evidence_history = history[-MAX_EVIDENCE_RECORDS_PER_SESSION:]

        return engine

    def get_turn_index(self, session_id: str) -> int:
        """Returns the current turn index for the session."""
        return self._session_turn_counts.get(session_id, 1)

    def advance_turn_index(self, session_id: str) -> int:
        """Increments and returns the updated turn index for the session."""
        current = self._session_turn_counts.get(session_id, 1)
        self._session_turn_counts[session_id] = current + 1
        return self._session_turn_counts[session_id]

    def clear_session(self, session_id: str) -> None:
        """Purges risk engine and evidence store for the specified session."""
        if session_id in self._session_engines:
            del self._session_engines[session_id]
        if session_id in self._session_turn_counts:
            del self._session_turn_counts[session_id]
        logger.info(f"Cleared evidence store and RiskEngine for session '{session_id}'.")

    def clear_all(self) -> None:
        """Clears all session evidence stores."""
        self._session_engines.clear()
        self._session_turn_counts.clear()


# Global evidence store singleton
default_evidence_store = SessionEvidenceStore()

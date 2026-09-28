import logging
from typing import Any, Dict, Optional

from app.ai_adapter import bootstrap_ai_root
from app.config import settings
from app.models import (
    RiskEngineError,
    RiskEngineFailedError,
    RiskEngineUnavailableError,
)
from app.services.evidence_store import SessionEvidenceStore, default_evidence_store

logger = logging.getLogger("trustshield-backend.ai_risk_adapter")


class AIRiskAdapter:
    """
    Thin backend adapter wrapping the existing TrustShield AI Master Hybrid Risk Engine
    located at D:\\TrustShield\\ai\\risk\\risk_engine.py.
    Does not duplicate scoring weights, safety policies, or temporal risk accumulation logic.
    """

    def __init__(self):
        self._initialized = False
        self._risk_engine_cls = None
        self._readiness_status = "UNAVAILABLE"

    def initialize(self) -> bool:
        """Initializes AI root path and loads the existing RiskEngine class."""
        try:
            if not bootstrap_ai_root():
                self._readiness_status = "UNAVAILABLE"
                return False

            # Import existing AI RiskEngine implementation
            from ai.risk.risk_engine import RiskEngine

            self._risk_engine_cls = RiskEngine

            self._initialized = True
            self._readiness_status = "READY"
            logger.info("AIRiskAdapter initialized successfully with Master Hybrid Risk Engine.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AIRiskAdapter: {e}", exc_info=True)
            self._readiness_status = "ERROR"
            self._initialized = False
            return False

    def is_available(self) -> bool:
        """Returns True if the risk adapter is ready and initialized."""
        if not self._initialized:
            return self.initialize()
        return self._initialized

    def get_readiness_status(self) -> str:
        """Returns readiness status string ('READY', 'UNAVAILABLE', 'ERROR')."""
        if not self._initialized:
            self.initialize()
        return self._readiness_status

    def evaluate_session_turn(
        self,
        session_id: str,
        conversation_analysis: Optional[Dict[str, Any]] = None,
        voice_analysis: Optional[Dict[str, Any]] = None,
        claim_verification: Optional[Dict[str, Any]] = None,
        session_context: Optional[Dict[str, Any]] = None,
        advance_turn: bool = True,
        evidence_store: SessionEvidenceStore = default_evidence_store
    ) -> Dict[str, Any]:
        """
        Evaluates session risk for an interaction turn using accumulated multi-modal evidence.
        """
        if not self.is_available() or self._risk_engine_cls is None:
            raise RiskEngineUnavailableError(
                "TrustShield AI Risk Engine service is unavailable. Check TRUSTSHIELD_AI_ROOT configuration."
            )

        try:
            engine = evidence_store.get_or_create_engine(session_id)
            turn_idx = evidence_store.get_turn_index(session_id)

            risk_result = engine.evaluate_turn(
                conversation_analysis=conversation_analysis,
                voice_analysis=voice_analysis,
                claim_verification=claim_verification,
                session_context=session_context,
                turn_index=turn_idx
            )

            # Advance turn index for session if requested
            if advance_turn:
                evidence_store.advance_turn_index(session_id)

            result_dict = dict(risk_result)
            result_dict["status"] = "available"
            return result_dict

        except Exception as e:
            logger.error(f"Error during Risk Engine evaluation for session {session_id}: {e}", exc_info=True)
            raise RiskEngineFailedError(f"Risk Engine evaluation failed: {str(e)}")


# Global adapter instance
default_risk_adapter = AIRiskAdapter()

import logging
from typing import Any, Dict, Optional

from app.ai_adapter import bootstrap_ai_root
from app.config import settings
from app.models import (
    ClaimVerificationError,
    ClaimVerificationFailedError,
    ClaimVerificationUnavailableError,
)

logger = logging.getLogger("trustshield-backend.ai_claim_adapter")


class AIClaimVerificationAdapter:
    """
    Thin backend adapter wrapping the existing TrustShield Official Claim Verifier
    located at D:\\TrustShield\\ai\\claim_verification\\claim_verifier.py.
    Extracts factual claims, retrieves live/static official sources, and performs 1-to-1 provenance verification.
    """

    def __init__(self):
        self._initialized = False
        self._verify_fn = None
        self._readiness_status = "UNAVAILABLE"

    def initialize(self) -> bool:
        """Initializes AI root path and loads the existing verify_official_claim function."""
        try:
            if not bootstrap_ai_root():
                self._readiness_status = "UNAVAILABLE"
                return False

            # Import existing AI verify_official_claim implementation
            from ai.claim_verification.claim_verifier import verify_official_claim

            self._verify_fn = verify_official_claim

            self._initialized = True
            self._readiness_status = "READY"
            logger.info("AIClaimVerificationAdapter initialized successfully with Official Claim Verifier.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AIClaimVerificationAdapter: {e}", exc_info=True)
            self._readiness_status = "ERROR"
            self._initialized = False
            return False

    def is_available(self) -> bool:
        """Returns True if the claim verification adapter is ready and initialized."""
        if not self._initialized:
            return self.initialize()
        return self._initialized

    def get_readiness_status(self) -> str:
        """Returns readiness status string ('READY', 'UNAVAILABLE', 'ERROR')."""
        if not self._initialized:
            self.initialize()
        return self._readiness_status

    def verify_claim(
        self,
        text: str,
        session_context: Optional[Dict[str, Any]] = None,
        simulate_live: bool = True
    ) -> Dict[str, Any]:
        """
        Extracts and verifies official claims from conversation text snippets against authoritative registries.
        """
        if not text or not text.strip():
            return {
                "status": "empty_input",
                "explanation": "No text provided for claim verification."
            }

        if not self.is_available() or self._verify_fn is None:
            raise ClaimVerificationUnavailableError(
                "TrustShield AI Claim Verification service is unavailable. Check TRUSTSHIELD_AI_ROOT configuration."
            )

        try:
            result = self._verify_fn(
                text.strip(),
                session_context=session_context,
                simulate_live=simulate_live
            )

            res_dict = result.to_dict() if hasattr(result, "to_dict") else dict(result)
            res_dict["status"] = "available"
            return res_dict

        except Exception as e:
            logger.error(f"Error during Official Claim Verification: {e}", exc_info=True)
            raise ClaimVerificationFailedError(f"Claim verification failed: {str(e)}")


# Global adapter instance
default_claim_adapter = AIClaimVerificationAdapter()

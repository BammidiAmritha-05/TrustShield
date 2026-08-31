import logging
from typing import Any, Dict, Optional

from app.ai_adapter import bootstrap_ai_root
from app.config import settings
from app.models import (
    ConversationIntelligenceError,
    ConversationIntelligenceFailedError,
    ConversationIntelligenceUnavailableError,
)

logger = logging.getLogger("trustshield-backend.ai_conversation_adapter")


class AIConversationAdapter:
    """
    Thin backend adapter wrapping the existing TrustShield AI conversation intelligence implementation
    located at D:\\TrustShield\\ai\\intelligence\\conversation_intelligence.py.
    Does not duplicate intent, action, manipulation, or impersonation classifiers or logic.
    """

    def __init__(self):
        self._initialized = False
        self._analyze_fn = None
        self._readiness_status = "UNAVAILABLE"

    def initialize(self) -> bool:
        """Initializes AI root path and loads the existing conversation intelligence service."""
        try:
            if not bootstrap_ai_root():
                self._readiness_status = "UNAVAILABLE"
                return False

            # Import existing AI conversation intelligence implementation
            from ai.intelligence.conversation_intelligence import analyze_conversation

            self._analyze_fn = analyze_conversation

            self._initialized = True
            self._readiness_status = "READY"
            logger.info("AIConversationAdapter initialized successfully with conversation intelligence engine.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AIConversationAdapter: {e}", exc_info=True)
            self._readiness_status = "ERROR"
            self._initialized = False
            return False

    def is_available(self) -> bool:
        """Returns True if the conversation intelligence adapter is ready and initialized."""
        if not self._initialized:
            return self.initialize()
        return self._initialized

    def get_readiness_status(self) -> str:
        """Returns readiness status string ('READY', 'UNAVAILABLE', 'ERROR')."""
        if not self._initialized:
            self.initialize()
        return self._readiness_status

    def analyze_text(
        self,
        text: str,
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyzes a conversation text snippet or transcript using the existing AI conversation intelligence engine.
        Returns a structured dictionary matching the underlying ConversationAnalysisResult.
        """
        if not text or not text.strip():
            return {
                "status": "empty_input",
                "explanation": "No text provided for conversation analysis."
            }

        if not self.is_available() or self._analyze_fn is None:
            raise ConversationIntelligenceUnavailableError(
                "TrustShield AI conversation intelligence service is unavailable. Check TRUSTSHIELD_AI_ROOT configuration."
            )

        try:
            # Invoke existing AI conversation intelligence function
            res = self._analyze_fn(text.strip(), session_context=session_context)
            res_dict = res.to_dict() if hasattr(res, "to_dict") else dict(res)
            res_dict["status"] = "available"
            return res_dict

        except Exception as e:
            logger.error(f"Error during conversation intelligence analysis: {e}", exc_info=True)
            raise ConversationIntelligenceFailedError(f"Conversation intelligence analysis failed: {str(e)}")


# Global adapter instance
default_conversation_adapter = AIConversationAdapter()

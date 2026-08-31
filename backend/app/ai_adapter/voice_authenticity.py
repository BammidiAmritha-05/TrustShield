import logging
import os
import tempfile
import wave
from typing import Any, Dict, Optional

from app.ai_adapter import bootstrap_ai_root
from app.config import settings
from app.models import (
    VoiceAuthenticityError,
    VoiceAuthenticityFailedError,
    VoiceAuthenticityUnavailableError,
)

logger = logging.getLogger("trustshield-backend.ai_voice_authenticity_adapter")


class AIVoiceAuthenticityAdapter:
    """
    Thin backend adapter wrapping the existing TrustShield AI AASIST-L voice authenticity implementation
    located at D:\\TrustShield\\ai\\voice_authenticity\\voice_authenticity_service.py.
    Does not duplicate AASIST-L architecture, checkpoint loading, or model code.
    """

    def __init__(self):
        self._initialized = False
        self._analyze_fn = None
        self._get_model_fn = None
        self._readiness_status = "UNAVAILABLE"

    def initialize(self) -> bool:
        """Initializes AI root path and loads the existing AASIST voice authenticity service."""
        try:
            if not bootstrap_ai_root():
                self._readiness_status = "UNAVAILABLE"
                return False

            # Import existing AI AASIST voice authenticity implementation
            from ai.voice_authenticity.voice_authenticity_service import (
                analyze_audio,
                get_aasist_model,
            )

            self._analyze_fn = analyze_audio
            self._get_model_fn = get_aasist_model

            # Warm up cached AASIST model
            self._get_model_fn()

            self._initialized = True
            self._readiness_status = "READY"
            logger.info("AIVoiceAuthenticityAdapter initialized successfully with AASIST-L model.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AIVoiceAuthenticityAdapter: {e}", exc_info=True)
            self._readiness_status = "ERROR"
            self._initialized = False
            return False

    def is_available(self) -> bool:
        """Returns True if the voice authenticity adapter is ready and initialized."""
        if not self._initialized:
            return self.initialize()
        return self._initialized

    def get_readiness_status(self) -> str:
        """Returns readiness status string ('READY', 'UNAVAILABLE', 'ERROR')."""
        if not self._initialized:
            self.initialize()
        return self._readiness_status

    def analyze_pcm_bytes(
        self,
        pcm_bytes: bytes,
        sample_rate: int = settings.TARGET_SAMPLE_RATE
    ) -> Dict[str, Any]:
        """
        Analyzes raw normalized 16-bit PCM bytes using AASIST-L voice anti-spoofing.
        Handles minimum audio duration bounds (< 0.5s / 8000 samples) without running inference.
        """
        if not pcm_bytes or len(pcm_bytes) == 0:
            return {
                "status": "insufficient_evidence",
                "reason": "audio_empty",
                "samples": 0,
                "duration_sec": 0.0
            }

        # 16-bit PCM mono = 2 bytes per sample. 8000 samples = 16000 bytes = 0.5 seconds at 16 kHz.
        samples_count = len(pcm_bytes) // 2
        if samples_count < 8000:
            return {
                "status": "insufficient_evidence",
                "reason": "audio_too_short",
                "samples": samples_count,
                "duration_sec": round(samples_count / float(sample_rate), 3)
            }

        if not self.is_available() or self._analyze_fn is None:
            raise VoiceAuthenticityUnavailableError(
                "TrustShield AI voice authenticity service is unavailable. Check TRUSTSHIELD_AI_ROOT configuration."
            )

        temp_wav_path = None

        try:
            # Write normalized PCM bytes into temporary WAV file for AASIST soundfile reader
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav_path = temp_wav.name

            with wave.open(temp_wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(pcm_bytes)

            # Invoke existing AI voice authenticity analyze_audio function
            result = self._analyze_fn(temp_wav_path)
            return result

        except Exception as e:
            logger.error(f"Error during AASIST voice authenticity inference: {e}", exc_info=True)
            raise VoiceAuthenticityFailedError(f"Voice authenticity analysis failed: {str(e)}")

        finally:
            # Purge temporary file immediately
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to remove temporary WAV file {temp_wav_path}: {cleanup_err}")


# Global adapter instance
default_voice_authenticity_adapter = AIVoiceAuthenticityAdapter()

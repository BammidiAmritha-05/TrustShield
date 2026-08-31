import io
import logging
import os
import tempfile
import wave
from typing import Any, Dict, Optional

from app.ai_adapter import bootstrap_ai_root
from app.config import settings
from app.models import (
    TranscriptionError,
    TranscriptionFailedError,
    TranscriptionUnavailableError,
)

logger = logging.getLogger("trustshield-backend.ai_transcription_adapter")


class AITranscriptionAdapter:
    """
    Thin backend adapter wrapping the existing TrustShield AI faster-whisper transcription implementation
    located at D:\\TrustShield\\ai\\transcription\\transcription_service.py.
    Does not recreate or duplicate faster-whisper logic.
    """

    def __init__(self):
        self._initialized = False
        self._transcribe_fn = None
        self._get_model_fn = None
        self._readiness_status = "UNAVAILABLE"

    def initialize(self) -> bool:
        """Initializes AI root path and imports the existing transcription service."""
        try:
            if not bootstrap_ai_root():
                self._readiness_status = "UNAVAILABLE"
                return False

            # Import existing AI transcription implementation
            from ai.transcription.transcription_service import (
                get_whisper_model,
                transcribe_audio,
            )

            self._transcribe_fn = transcribe_audio
            self._get_model_fn = get_whisper_model

            # Warm up cached model
            model_size = settings.WHISPER_MODEL_SIZE
            self._get_model_fn(model_size=model_size, device="cpu", compute_type="int8")

            self._initialized = True
            self._readiness_status = "READY"
            logger.info(f"AITranscriptionAdapter initialized successfully with model '{model_size}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AITranscriptionAdapter: {e}", exc_info=True)
            self._readiness_status = "ERROR"
            self._initialized = False
            return False

    def is_available(self) -> bool:
        """Returns True if the transcription adapter is ready and initialized."""
        if not self._initialized:
            return self.initialize()
        return self._initialized

    def get_readiness_status(self) -> str:
        """Returns readiness status string ('READY', 'UNAVAILABLE', 'ERROR')."""
        if not self._initialized:
            self.initialize()
        return self._readiness_status

    def transcribe_pcm_bytes(
        self,
        pcm_bytes: bytes,
        sample_rate: int = settings.TARGET_SAMPLE_RATE,
        model_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes raw normalized 16-bit PCM bytes by writing a temporary WAV file,
        invoking the existing AI transcription implementation, and purging the temp file.
        """
        if not pcm_bytes or len(pcm_bytes) == 0:
            raise TranscriptionFailedError("PCM audio bytes payload is empty.")

        if not self.is_available() or self._transcribe_fn is None:
            raise TranscriptionUnavailableError(
                "TrustShield AI transcription service is unavailable. Check TRUSTSHIELD_AI_ROOT configuration."
            )

        target_model_size = model_size or settings.WHISPER_MODEL_SIZE
        temp_wav_path = None

        try:
            # Write normalized PCM bytes into temporary WAV file for faster-whisper file-based input
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav_path = temp_wav.name

            with wave.open(temp_wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(pcm_bytes)

            # Invoke existing AI transcription service function
            result = self._transcribe_fn(temp_wav_path, model_size=target_model_size)
            return result

        except Exception as e:
            logger.error(f"Error during AI transcription inference: {e}", exc_info=True)
            raise TranscriptionFailedError(f"Transcription inference failed: {str(e)}")

        finally:
            # Purge temporary file immediately
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to remove temporary WAV file {temp_wav_path}: {cleanup_err}")


# Global adapter instance
default_transcription_adapter = AITranscriptionAdapter()

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator


class InteractionType(str, Enum):
    VOICE = "voice"
    TEXT = "text"
    DEMO = "demo"


class SessionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    ENDED = "ended"


class SessionCreateRequest(BaseModel):
    interaction_type: InteractionType
    consent: bool = Field(..., description="Explicit user consent required")

    @field_validator("consent")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("Explicit consent (true) is required to start a protection session.")
        return v

    model_config = {
        "extra": "forbid"
    }


class EventMetadata(BaseModel):
    event_type: str
    timestamp: datetime
    details: Dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    session_id: str
    status: SessionStatus
    interaction_type: InteractionType
    consent: bool
    created_at: datetime
    ended_at: Optional[datetime] = None
    event_count: int = 0


class WSEventType(str, Enum):
    SESSION_STARTED = "SESSION_STARTED"
    TEXT_RECEIVED = "TEXT_RECEIVED"
    BINARY_RECEIVED = "BINARY_RECEIVED"
    AUDIO_BUFFERED = "AUDIO_BUFFERED"
    AUDIO_DECODED = "AUDIO_DECODED"
    TRANSCRIPT_PARTIAL = "TRANSCRIPT_PARTIAL"
    TRANSCRIPT_FINAL = "TRANSCRIPT_FINAL"
    VOICE_ANALYSIS = "VOICE_ANALYSIS"
    SIGNAL_UPDATE = "SIGNAL_UPDATE"
    RISK_UPDATE = "RISK_UPDATE"
    CLAIM_VERIFICATION = "CLAIM_VERIFICATION"
    PROTECTION_UPDATE = "PROTECTION_UPDATE"
    ERROR = "ERROR"
    SESSION_ENDED = "SESSION_ENDED"


class WSServerEvent(BaseModel):
    type: WSEventType
    version: int = 1
    session_id: str
    timestamp: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class DecodedAudio(BaseModel):
    sample_rate: int
    channels: int
    sample_width: int
    sample_count: int
    duration_seconds: float
    format: str = "pcm_s16le"
    codec: str = "pcm_s16le"
    pcm_data: bytes = Field(default=b"", exclude=True)

    def to_metadata_payload(self) -> Dict[str, Any]:
        """Returns safe metadata dictionary for WebSocket event payloads (excluding raw PCM)."""
        return {
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "sample_width": self.sample_width,
            "sample_count": self.sample_count,
            "duration_seconds": round(self.duration_seconds, 3),
            "format": self.format,
            "codec": self.codec
        }


# Custom Application Exceptions for Audio Buffer
class AudioBufferError(Exception):
    """Base exception for audio buffer operations."""
    pass


class EmptyAudioChunkError(AudioBufferError):
    """Raised when an empty audio chunk is submitted."""
    pass


class AudioChunkTooLargeError(AudioBufferError):
    """Raised when an audio chunk exceeds maximum permitted chunk bytes."""
    pass


class SessionAudioLimitExceededError(AudioBufferError):
    """Raised when adding a chunk would exceed maximum permitted session audio buffer size."""
    pass


# Custom Application Exceptions for Audio Decoder
class DecoderError(Exception):
    """Base exception for audio decoding operations."""
    pass


class EmptyAudioError(DecoderError):
    """Raised when input audio data for decoding is empty."""
    pass


class UnsupportedAudioFormatError(DecoderError):
    """Raised when the audio format/container is unsupported."""
    pass


class AudioDecodeFailedError(DecoderError):
    """Raised when audio decoding fails on malformed input."""
    pass


class AudioDurationInvalidError(DecoderError):
    """Raised when decoded audio duration or sample count is invalid (<= 0)."""
    pass


class AudioDurationTooLongError(DecoderError):
    """Raised when decoded audio duration exceeds MAX_AUDIO_DURATION_SECONDS."""
    pass


# Custom Application Exceptions for AI Transcription
class TranscriptionError(Exception):
    """Base exception for AI transcription operations."""
    pass


class TranscriptionUnavailableError(TranscriptionError):
    """Raised when AI root or transcription module is unavailable."""
    pass


class TranscriptionFailedError(TranscriptionError):
    """Raised when AI transcription inference fails."""
    pass


# Custom Application Exceptions for Voice Authenticity
class VoiceAuthenticityError(Exception):
    """Base exception for voice authenticity operations."""
    pass


class VoiceAuthenticityUnavailableError(VoiceAuthenticityError):
    """Raised when AI root or voice authenticity module is unavailable."""
    pass


class VoiceAuthenticityFailedError(VoiceAuthenticityError):
    """Raised when voice authenticity inference fails."""
    pass


# Custom Application Exceptions for Conversation Intelligence
class ConversationIntelligenceError(Exception):
    """Base exception for conversation intelligence operations."""
    pass


class ConversationIntelligenceUnavailableError(ConversationIntelligenceError):
    """Raised when AI root or conversation intelligence module is unavailable."""
    pass


class ConversationIntelligenceFailedError(ConversationIntelligenceError):
    """Raised when conversation intelligence analysis fails."""
    pass


# Custom Application Exceptions for Risk Engine
class RiskEngineError(Exception):
    """Base exception for Risk Engine operations."""
    pass


class RiskEngineUnavailableError(RiskEngineError):
    """Raised when AI root or Risk Engine module is unavailable."""
    pass


class RiskEngineFailedError(RiskEngineError):
    """Raised when risk evaluation fails."""
    pass


# Custom Application Exceptions for Protection Agent
class ProtectionAgentError(Exception):
    """Base exception for Protection Agent operations."""
    pass


class ProtectionAgentUnavailableError(ProtectionAgentError):
    """Raised when AI root or Protection Agent module is unavailable."""
    pass


class ProtectionAgentFailedError(ProtectionAgentError):
    """Raised when protection guidance generation fails."""
    pass


# Custom Application Exceptions for Claim Verification
class ClaimVerificationError(Exception):
    """Base exception for Claim Verification operations."""
    pass


class ClaimVerificationUnavailableError(ClaimVerificationError):
    """Raised when AI root or Claim Verification module is unavailable."""
    pass


class ClaimVerificationFailedError(ClaimVerificationError):
    """Raised when claim verification execution fails."""
    pass

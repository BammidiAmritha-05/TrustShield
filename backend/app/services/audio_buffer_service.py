from datetime import datetime, timezone
import threading
from typing import Any, Dict, Optional

from app.config import settings
from app.models import (
    AudioChunkTooLargeError,
    EmptyAudioChunkError,
    SessionAudioLimitExceededError,
)


class AudioBufferService:
    """
    Thread-safe in-memory temporary audio buffer service.
    Manages raw binary audio chunks per session prior to future AI processing.
    Enforces strict chunk size and total session buffer memory limits.
    """

    def __init__(
        self,
        max_chunk_bytes: int = settings.MAX_AUDIO_CHUNK_BYTES,
        max_session_bytes: int = settings.MAX_SESSION_AUDIO_BYTES,
    ):
        self.max_chunk_bytes = max_chunk_bytes
        self.max_session_bytes = max_session_bytes
        self._buffers: Dict[str, bytearray] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def append_chunk(self, session_id: str, data: bytes) -> Dict[str, Any]:
        """Appends a binary chunk to the specified session buffer after validation."""
        if not data or len(data) == 0:
            raise EmptyAudioChunkError("Binary audio chunk cannot be empty.")

        chunk_size = len(data)
        if chunk_size > self.max_chunk_bytes:
            raise AudioChunkTooLargeError(
                f"Audio chunk size ({chunk_size} bytes) exceeds maximum limit of {self.max_chunk_bytes} bytes."
            )

        with self._lock:
            current_buffer = self._buffers.get(session_id, bytearray())
            current_total = len(current_buffer)

            if current_total + chunk_size > self.max_session_bytes:
                raise SessionAudioLimitExceededError(
                    f"Adding chunk of {chunk_size} bytes exceeds maximum session audio limit of {self.max_session_bytes} bytes."
                )

            now = datetime.now(timezone.utc)

            # Append chunk data
            current_buffer.extend(data)
            self._buffers[session_id] = current_buffer

            # Update metadata
            meta = self._metadata.get(session_id, {
                "session_id": session_id,
                "chunk_count": 0,
                "total_bytes": 0,
                "first_chunk_at": now,
                "last_chunk_at": now
            })

            meta["chunk_count"] += 1
            meta["total_bytes"] = len(current_buffer)
            meta["last_chunk_at"] = now
            self._metadata[session_id] = meta

            return {
                "bytes": chunk_size,
                "total_buffered_bytes": meta["total_bytes"],
                "chunk_count": meta["chunk_count"]
            }

    def get_buffer(self, session_id: str) -> bytes:
        """Retrieves a snapshot copy of the buffered raw bytes for a session."""
        with self._lock:
            buf = self._buffers.get(session_id)
            return bytes(buf) if buf else b""

    def get_size(self, session_id: str) -> int:
        """Returns the current total byte count buffered for a session."""
        with self._lock:
            buf = self._buffers.get(session_id)
            return len(buf) if buf else 0

    def get_metadata(self, session_id: str) -> Dict[str, Any]:
        """Returns safe metadata summary for a session buffer."""
        with self._lock:
            meta = self._metadata.get(session_id)
            if not meta:
                return {
                    "session_id": session_id,
                    "chunk_count": 0,
                    "total_bytes": 0,
                    "first_chunk_at": None,
                    "last_chunk_at": None
                }
            return meta.copy()

    def clear_buffer(self, session_id: str) -> None:
        """Purges and clears the audio buffer and metadata for a session."""
        with self._lock:
            if session_id in self._buffers:
                del self._buffers[session_id]
            if session_id in self._metadata:
                del self._metadata[session_id]

    def clear_all(self) -> None:
        """Utility method to clear all session buffers (for testing reset)."""
        with self._lock:
            self._buffers.clear()
            self._metadata.clear()


# Global audio buffer service instance
default_audio_buffer_service = AudioBufferService()

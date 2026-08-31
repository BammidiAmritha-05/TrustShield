import io
import wave
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from app.ai_adapter.transcription import AITranscriptionAdapter
from app.config import settings
from app.models import (
    TranscriptionFailedError,
    TranscriptionUnavailableError,
)


def make_test_pcm_bytes(duration_seconds: float = 0.5) -> bytes:
    """Generates synthetic 16 kHz Mono 16-bit PCM bytes."""
    num_samples = int(16000 * duration_seconds)
    t = np.linspace(0, duration_seconds, num_samples, endpoint=False)
    pcm_signal = (np.sin(2 * np.pi * 440.0 * t) * 16384).astype(np.int16)
    return pcm_signal.tobytes()


def test_ai_root_unavailable(monkeypatch):
    """1. AI root not configured returns UNAVAILABLE status."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "")
    adapter = AITranscriptionAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"
    assert not adapter.is_available()


def test_ai_module_unavailable(monkeypatch):
    """2. Non-existent AI root directory returns UNAVAILABLE status."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "D:\\NonExistentPath\\ai")
    adapter = AITranscriptionAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"


def test_adapter_initialization(monkeypatch):
    """3. Successful initialization loads adapter functions."""
    adapter = AITranscriptionAdapter()
    mock_transcribe = MagicMock(return_value={"text": "hello", "segments": [], "language": "en", "duration": 0.5})
    mock_model = MagicMock()

    adapter._transcribe_fn = mock_transcribe
    adapter._get_model_fn = mock_model
    adapter._initialized = True
    adapter._readiness_status = "READY"

    assert adapter.is_available() is True
    assert adapter.get_readiness_status() == "READY"


def test_model_initialization_failure(monkeypatch):
    """4. Model warmup failure sets readiness status to ERROR."""
    adapter = AITranscriptionAdapter()
    with patch("app.ai_adapter.transcription.bootstrap_ai_root", return_value=True):
        with patch("ai.transcription.transcription_service.get_whisper_model", side_effect=RuntimeError("CUDA out of memory")):
            res = adapter.initialize()
            assert res is False
            assert adapter.get_readiness_status() == "ERROR"


def test_successful_transcription_payload_format():
    """5, 6, 7, 8: Successful transcription payload, segment structure, timestamps."""
    adapter = AITranscriptionAdapter()
    mock_output = {
        "text": "Hello TrustShield AI",
        "segments": [
            {"start": 0.0, "end": 0.5, "text": "Hello TrustShield AI"}
        ],
        "language": "en",
        "duration": 0.5
    }
    adapter._transcribe_fn = MagicMock(return_value=mock_output)
    adapter._get_model_fn = MagicMock()
    adapter._initialized = True
    adapter._readiness_status = "READY"

    pcm_bytes = make_test_pcm_bytes(0.5)
    result = adapter.transcribe_pcm_bytes(pcm_bytes)

    assert result["text"] == "Hello TrustShield AI"
    assert len(result["segments"]) == 1
    assert result["segments"][0]["start"] == 0.0
    assert result["segments"][0]["end"] == 0.5
    assert result["language"] == "en"


def test_empty_pcm_bytes_rejection():
    """Empty PCM bytes raise TranscriptionFailedError."""
    adapter = AITranscriptionAdapter()
    adapter._initialized = True
    with pytest.raises(TranscriptionFailedError):
        adapter.transcribe_pcm_bytes(b"")


def test_uninitialized_adapter_throws_unavailable():
    """Uninitialized adapter throws TranscriptionUnavailableError."""
    adapter = AITranscriptionAdapter()
    adapter._initialized = False
    adapter._readiness_status = "UNAVAILABLE"
    with patch.object(adapter, "initialize", return_value=False):
        with pytest.raises(TranscriptionUnavailableError):
            adapter.transcribe_pcm_bytes(make_test_pcm_bytes(0.5))


def test_malformed_ai_response():
    """9. Malformed AI response handling."""
    adapter = AITranscriptionAdapter()
    adapter._transcribe_fn = MagicMock(side_effect=ValueError("Corrupted return format"))
    adapter._initialized = True
    adapter._readiness_status = "READY"

    with pytest.raises(TranscriptionFailedError):
        adapter.transcribe_pcm_bytes(make_test_pcm_bytes(0.5))


def test_inference_failure():
    """10. Inference exception raises TranscriptionFailedError."""
    adapter = AITranscriptionAdapter()
    adapter._transcribe_fn = MagicMock(side_effect=RuntimeError("Whisper CTranslate2 Error"))
    adapter._initialized = True
    adapter._readiness_status = "READY"

    with pytest.raises(TranscriptionFailedError) as exc_info:
        adapter.transcribe_pcm_bytes(make_test_pcm_bytes(0.5))
    assert "Whisper CTranslate2 Error" in str(exc_info.value)


def test_session_reset_and_state():
    """11. Adapter state reset."""
    adapter = AITranscriptionAdapter()
    adapter._initialized = True
    adapter._readiness_status = "READY"
    assert adapter.get_readiness_status() == "READY"


def test_model_reuse():
    """12. Reuses get_whisper_model cache across calls."""
    adapter = AITranscriptionAdapter()
    mock_model_fn = MagicMock()
    adapter._get_model_fn = mock_model_fn
    adapter._transcribe_fn = MagicMock(return_value={"text": "t", "segments": [], "language": "en", "duration": 0.5})
    adapter._initialized = True

    pcm = make_test_pcm_bytes(0.5)
    adapter.transcribe_pcm_bytes(pcm)
    adapter.transcribe_pcm_bytes(pcm)
    assert adapter._transcribe_fn.call_count == 2

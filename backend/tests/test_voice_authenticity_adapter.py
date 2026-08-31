import pytest
from unittest.mock import patch, MagicMock
import numpy as np

from app.ai_adapter.voice_authenticity import AIVoiceAuthenticityAdapter
from app.config import settings
from app.models import (
    VoiceAuthenticityFailedError,
    VoiceAuthenticityUnavailableError,
)


def make_test_pcm_bytes(duration_seconds: float = 1.0) -> bytes:
    """Generates synthetic 16 kHz Mono 16-bit PCM bytes."""
    num_samples = int(16000 * duration_seconds)
    t = np.linspace(0, duration_seconds, num_samples, endpoint=False)
    pcm_signal = (np.sin(2 * np.pi * 440.0 * t) * 16384).astype(np.int16)
    return pcm_signal.tobytes()


def test_adapter_import_and_instantiation():
    """1. Adapter import and default initialization."""
    adapter = AIVoiceAuthenticityAdapter()
    assert adapter is not None


def test_ai_root_missing(monkeypatch):
    """2. AI root missing sets readiness status to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "")
    adapter = AIVoiceAuthenticityAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"
    assert not adapter.is_available()


def test_ai_module_unavailable(monkeypatch):
    """3. Non-existent AI root directory sets readiness status to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "D:\\NonExistentPath\\ai")
    adapter = AIVoiceAuthenticityAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"


def test_insufficient_audio_boundary():
    """4 & 10. Chunks < 0.5s (8000 samples) return insufficient_evidence without fabricated score."""
    adapter = AIVoiceAuthenticityAdapter()
    short_pcm = make_test_pcm_bytes(duration_seconds=0.3)  # ~4800 samples

    res = adapter.analyze_pcm_bytes(short_pcm)
    assert res["status"] == "insufficient_evidence"
    assert res["reason"] == "audio_too_short"
    assert "synthetic_score" not in res  # No fabricated score!


def test_valid_ai_response():
    """5, 6, 7. Valid AI model response score semantics and range."""
    adapter = AIVoiceAuthenticityAdapter()
    mock_ai_output = {
        "status": "available",
        "bona_fide_score": 2.14,
        "synthetic_score": 0.18,
        "bona_fide_probability": 0.82,
        "quality": "good",
        "rms_energy": 0.05,
        "spectral_flatness": 0.12,
        "input_duration_sec": 1.0
    }
    adapter._analyze_fn = MagicMock(return_value=mock_ai_output)
    adapter._get_model_fn = MagicMock()
    adapter._initialized = True
    adapter._readiness_status = "READY"

    pcm_bytes = make_test_pcm_bytes(duration_seconds=1.0)
    res = adapter.analyze_pcm_bytes(pcm_bytes)

    assert res["status"] == "available"
    assert res["synthetic_score"] == 0.18
    assert res["bona_fide_score"] == 2.14
    assert 0.0 <= res["synthetic_score"] <= 1.0
    assert res["quality"] == "good"


def test_uninitialized_adapter_throws_unavailable():
    """Uninitialized adapter throws VoiceAuthenticityUnavailableError."""
    adapter = AIVoiceAuthenticityAdapter()
    adapter._initialized = False
    adapter._readiness_status = "UNAVAILABLE"
    with patch.object(adapter, "initialize", return_value=False):
        with pytest.raises(VoiceAuthenticityUnavailableError):
            adapter.analyze_pcm_bytes(make_test_pcm_bytes(1.0))


def test_malformed_ai_response():
    """8. Exception in underlying AI code raises VoiceAuthenticityFailedError."""
    adapter = AIVoiceAuthenticityAdapter()
    adapter._analyze_fn = MagicMock(side_effect=ValueError("Corrupted PyTorch tensor"))
    adapter._initialized = True
    adapter._readiness_status = "READY"

    with pytest.raises(VoiceAuthenticityFailedError):
        adapter.analyze_pcm_bytes(make_test_pcm_bytes(1.0))


def test_inference_exception():
    """9. PyTorch inference error raises VoiceAuthenticityFailedError."""
    adapter = AIVoiceAuthenticityAdapter()
    adapter._analyze_fn = MagicMock(side_effect=RuntimeError("PyTorch execution error"))
    adapter._initialized = True
    adapter._readiness_status = "READY"

    with pytest.raises(VoiceAuthenticityFailedError) as exc_info:
        adapter.analyze_pcm_bytes(make_test_pcm_bytes(1.0))
    assert "PyTorch execution error" in str(exc_info.value)


def test_model_initialization_failure():
    """Model warmup failure sets readiness to ERROR."""
    adapter = AIVoiceAuthenticityAdapter()
    with patch("app.ai_adapter.voice_authenticity.bootstrap_ai_root", return_value=True):
        with patch("ai.voice_authenticity.voice_authenticity_service.get_aasist_model", side_effect=RuntimeError("PyTorch load error")):
            res = adapter.initialize()
            assert res is False
            assert adapter.get_readiness_status() == "ERROR"


def test_model_reuse_behavior():
    """11. Reuses get_aasist_model cache across calls."""
    adapter = AIVoiceAuthenticityAdapter()
    adapter._get_model_fn = MagicMock()
    adapter._analyze_fn = MagicMock(return_value={"status": "available", "synthetic_score": 0.1})
    adapter._initialized = True

    pcm = make_test_pcm_bytes(1.0)
    adapter.analyze_pcm_bytes(pcm)
    adapter.analyze_pcm_bytes(pcm)
    assert adapter._analyze_fn.call_count == 2

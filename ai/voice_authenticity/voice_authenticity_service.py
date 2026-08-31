"""
Voice Authenticity Service utilizing AASIST-L for Audio Anti-Spoofing.

Model Source: SpeechAntiSpoofingBenchmarks/AASIST-L (Hugging Face)
License: MIT
"""

import os
import importlib.util
from typing import Dict, Any, Optional
import numpy as np
import soundfile as sf
import scipy.signal as signal
import torch
import torch.nn.functional as F
from huggingface_hub import hf_hub_download
import torchaudio

_CUT = 64600  # AASIST-L fixed sample length
_HF_REPO = "SpeechAntiSpoofingBenchmarks/AASIST-L"

_D_ARGS = {
    "architecture": "AASIST",
    "nb_samp": 64600,
    "first_conv": 128,
    "filts": [70, [1, 32], [32, 32], [32, 24], [24, 24]],
    "gat_dims": [24, 32],
    "pool_ratios": [0.4, 0.5, 0.7, 0.5],
    "temperatures": [2.0, 2.0, 100.0, 100.0],
}

_aasist_model_cache: Optional[torch.nn.Module] = None


def get_aasist_model() -> torch.nn.Module:
    """Loads and caches the AASIST-L PyTorch model from Hugging Face."""
    global _aasist_model_cache
    if _aasist_model_cache is None:
        net_path = hf_hub_download(repo_id=_HF_REPO, filename="_net.py")
        weights_path = hf_hub_download(repo_id=_HF_REPO, filename="AASIST-L.pth")

        spec = importlib.util.spec_from_file_location("_net", net_path)
        net_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(net_module)

        model = net_module.Model(_D_ARGS)
        sd = torch.load(weights_path, map_location="cpu")
        sd = sd.get("state_dict", sd) if isinstance(sd, dict) else sd
        model.load_state_dict(sd, strict=True)
        model.eval()
        _aasist_model_cache = model
    return _aasist_model_cache


def pad_fixed(x: np.ndarray, max_len: int = _CUT) -> np.ndarray:
    """Deterministic eval window: first max_len samples; tile-repeat if shorter.
    Matches clovaai/aasist data_utils.pad() used for dev/eval.
    """
    x = np.asarray(x, dtype=np.float32).reshape(-1)
    n = x.shape[0]
    if n >= max_len:
        return x[:max_len]
    reps = max_len // n + 1
    return np.tile(x, reps)[:max_len].astype(np.float32)


def preprocess_audio(audio_path: str) -> tuple[np.ndarray, int]:
    """Loads audio via soundfile, converts to 16 kHz mono float32."""
    data, sr = sf.read(audio_path, dtype="float32")
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    if sr != 16000:
        waveform = torch.from_numpy(data).unsqueeze(0)
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
        waveform = resampler(waveform)
        data = waveform.squeeze(0).numpy()
        sr = 16000
    return data.astype(np.float32), sr


def compute_spectral_flatness(audio_np: np.ndarray, sr: int = 16000) -> float:
    """Computes spectral flatness ratio (1.0 = white noise, ~0.0 = tonal speech)."""
    nperseg = min(len(audio_np), 1024)
    if nperseg < 64:
        return 1.0
    _freqs, psd = signal.welch(audio_np, fs=sr, nperseg=nperseg)
    psd = psd + 1e-12
    geo_mean = float(np.exp(np.mean(np.log(psd))))
    ari_mean = float(np.mean(psd))
    return float(geo_mean / ari_mean)


def analyze_audio(audio_path: str) -> Dict[str, Any]:
    """Analyzes an audio file using AASIST-L for voice anti-spoofing with audio quality gating.

    Args:
        audio_path: Path to the WAV/audio file.

    Returns:
        Dict containing status, bona_fide_score, synthetic_score, and quality.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    audio_np, sr = preprocess_audio(audio_path)
    num_samples = len(audio_np)

    # 1. Short audio boundary check (< 0.5 sec / 8000 samples)
    if num_samples < 8000:
        return {
            "status": "insufficient_evidence",
            "reason": "audio_too_short",
            "samples": num_samples,
            "duration_sec": round(num_samples / 16000, 3)
        }

    # 2. Silence / low-energy boundary check (RMS < 0.001)
    rms = float(np.sqrt(np.mean(np.square(audio_np))))
    if rms < 0.001:
        return {
            "status": "insufficient_evidence",
            "reason": "silence_or_low_energy",
            "rms_energy": round(rms, 6)
        }

    # 3. Unusable audio / Noise gate check (Spectral Flatness > 0.85)
    spectral_flatness = compute_spectral_flatness(audio_np, sr=sr)
    if spectral_flatness > 0.85:
        return {
            "status": "insufficient_evidence",
            "reason": "unusable_audio",
            "spectral_flatness": round(spectral_flatness, 4),
            "note": "Audio lacks speech structure and resembles unstructured white/colored noise."
        }

    # 4. Model inference for usable speech audio
    model = get_aasist_model()
    padded_audio = pad_fixed(audio_np, max_len=_CUT)
    input_tensor = torch.from_numpy(padded_audio).unsqueeze(0)

    with torch.no_grad():
        _hidden, logits = model(input_tensor)
        probs = F.softmax(logits, dim=-1)

    raw_bona_fide_score = float(logits[0, 1].item())
    synthetic_prob = float(probs[0, 0].item())
    bona_fide_prob = float(probs[0, 1].item())

    # Determine signal quality assessment
    quality = "good" if rms > 0.01 and num_samples >= 16000 else "acceptable"

    return {
        "status": "available",
        "bona_fide_score": round(raw_bona_fide_score, 4),
        "synthetic_score": round(synthetic_prob, 4),
        "bona_fide_probability": round(bona_fide_prob, 4),
        "quality": quality,
        "rms_energy": round(rms, 5),
        "spectral_flatness": round(spectral_flatness, 4),
        "input_duration_sec": round(num_samples / 16000, 2)
    }

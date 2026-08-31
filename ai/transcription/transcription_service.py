"""
Transcription Service utilizing faster-whisper on CPU.
"""

import os
from typing import Dict, Any, Optional
from faster_whisper import WhisperModel
import soundfile as sf

_model_cache: Dict[str, WhisperModel] = {}


def get_whisper_model(model_size: str = "tiny", device: str = "cpu", compute_type: str = "int8") -> WhisperModel:
    """Retrieve or initialize a cached WhisperModel instance."""
    cache_key = f"{model_size}_{device}_{compute_type}"
    if cache_key not in _model_cache:
        _model_cache[cache_key] = WhisperModel(model_size, device=device, compute_type=compute_type)
    return _model_cache[cache_key]


def transcribe_audio(audio_path: str, model_size: str = "tiny") -> Dict[str, Any]:
    """Transcribes an audio file using faster-whisper.

    Args:
        audio_path: Path to the WAV/audio file.
        model_size: Whisper model size ('tiny', 'base', etc.).

    Returns:
        Dict containing text, language, duration, and segment details.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Inspect audio metadata
    info = sf.info(audio_path)
    audio_duration = info.duration

    model = get_whisper_model(model_size=model_size, device="cpu", compute_type="int8")
    segments_gen, transcribe_info = model.transcribe(audio_path, beam_size=5)

    segments_list = []
    full_text_parts = []

    for seg in segments_gen:
        full_text_parts.append(seg.text)
        segments_list.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip()
        })

    full_text = " ".join(full_text_parts).strip()

    return {
        "text": full_text,
        "segments": segments_list,
        "language": transcribe_info.language,
        "duration": round(audio_duration, 2)
    }

"""
CLI Verification Script for Whisper Transcription Service (Phase 1 Part A).
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import json
import soundfile as sf
from ai.transcription.transcription_service import get_whisper_model, transcribe_audio


def main():
    print("=== STARTING WHISPER TRANSCRIPTION BENCHMARK ===")
    audio_path = os.path.join("tests", "audio", "real_voice.wav")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Missing audio test file: {audio_path}")

    # Inspect audio file properties
    info = sf.info(audio_path)
    print(f"Audio File     : {audio_path}")
    print(f"Duration       : {info.duration:.2f} seconds")
    print(f"Sample Rate    : {info.samplerate} Hz")
    print(f"Channels       : {info.channels}")
    print(f"Format         : {info.format} ({info.subtype})")

    # Measure model instantiation load time
    t0 = time.perf_counter()
    _model = get_whisper_model(model_size="tiny", device="cpu", compute_type="int8")
    t1 = time.perf_counter()
    load_time_sec = t1 - t0
    print(f"Model Load Time: {load_time_sec * 1000:.2f} ms")

    # Measure transcription latency
    t2 = time.perf_counter()
    result = transcribe_audio(audio_path, model_size="tiny")
    t3 = time.perf_counter()
    transcribe_time_sec = t3 - t2
    print(f"Transcribe Time: {transcribe_time_sec * 1000:.2f} ms")
    print("\n--- Transcription Result ---")
    print(json.dumps(result, indent=2))

    # Save results to docs/PHASE1_WHISPER_TEST.md
    doc_path = os.path.join("docs", "PHASE1_WHISPER_TEST.md")
    os.makedirs("docs", exist_ok=True)
    doc_content = f"""# Phase 1: Whisper Transcription Test Results

## Test Summary
- **Audio File**: `{audio_path}`
- **Audio Duration**: `{info.duration:.2f}` seconds
- **Sample Rate**: `{info.samplerate}` Hz
- **Channels**: `{info.channels}`
- **Audio Format**: `{info.format}` (`{info.subtype}`)

## Performance Benchmarks
- **Model Size**: `tiny` (`cpu`, `int8`)
- **Model Load Time**: `{load_time_sec * 1000:.2f}` ms
- **Transcription Latency**: `{transcribe_time_sec * 1000:.2f}` ms
- **Real-Time Factor (RTF)**: `{transcribe_time_sec / info.duration:.4f}`

## Output JSON Result
```json
{json.dumps(result, indent=2)}
```
"""
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc_content)
    print(f"\nSaved test report to {doc_path}")


if __name__ == "__main__":
    main()

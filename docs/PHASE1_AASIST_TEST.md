# Phase 1: AASIST-L Voice Anti-Spoofing Test Results

## Model Specifications
- **Model Repo**: `SpeechAntiSpoofingBenchmarks/AASIST-L` (Hugging Face)
- **Parameters**: 85,306 (FP32)
- **License**: MIT
- **Input Window**: 64,600 raw mono 16 kHz audio samples (~4.04 seconds)
- **Model Load Latency**: `1131.02` ms

## Verification & Semantics Confirmation
- **Logit Index 1**: Raw Bona Fide logit score (higher values = more genuine human voice).
- **Derived Signal**: Softmax probability over `[spoof, bona_fide]` yielding `synthetic_score` (0.0 to 1.0) labelled as **VOICE AUTHENTICITY SIGNAL**.

## Evaluation Results Matrix

```json
{
  "Real Voice": {
    "status": "available",
    "bona_fide_score": 1.8531,
    "synthetic_score": 0.037,
    "bona_fide_probability": 0.963,
    "quality": "good",
    "rms_energy": 0.02046,
    "spectral_flatness": 0.0285,
    "input_duration_sec": 3.26,
    "inference_latency_ms": 352.21
  },
  "Spoof Voice": {
    "status": "available",
    "bona_fide_score": -1.561,
    "synthetic_score": 0.9632,
    "bona_fide_probability": 0.0368,
    "quality": "good",
    "rms_energy": 0.48581,
    "spectral_flatness": 0.1002,
    "input_duration_sec": 3.5,
    "inference_latency_ms": 425.57
  },
  "Silence Test": {
    "status": "insufficient_evidence",
    "reason": "silence_or_low_energy",
    "rms_energy": 2.2e-05,
    "inference_latency_ms": 13.91
  },
  "Short Audio Test": {
    "status": "insufficient_evidence",
    "reason": "audio_too_short",
    "samples": 3200,
    "duration_sec": 0.2,
    "inference_latency_ms": 13.46
  },
  "Noisy Audio Test": {
    "status": "insufficient_evidence",
    "reason": "unusable_audio",
    "spectral_flatness": 0.9913,
    "note": "Audio lacks speech structure and resembles unstructured white/colored noise.",
    "inference_latency_ms": 24.79
  }
}
```

## Summary of Audio Quality Checks
1. **Real Speech (`real_voice.wav`)**: `bona_fide_score = 1.8531`, `synthetic_score = 0.037` -> **Bona Fide Human Voice**.
2. **Synthetic/Spoof (`spoof_voice.wav`)**: `bona_fide_score = -1.561`, `synthetic_score = 0.9632` -> **Synthetic/Spoof Detected**.
3. **Silence (`silence.wav`)**: Status = `insufficient_evidence` (`reason = silence_or_low_energy`).
4. **Short Audio (`short.wav`)**: Status = `insufficient_evidence` (`reason = audio_too_short`).
5. **Noisy Audio (`noisy.wav`)**: Analyzed safely without crash (`synthetic_score = None`).

# Model Provenance & Specification Document

This document records the exact provenance, licenses, architectural parameters, inputs, outputs, and operational limitations for all AI models integrated into TrustShield.

---

## 1. faster-whisper (Speech-to-Text Transcription)

- **Model Name**: faster-whisper (`tiny` / `base`)
- **Source Repository**: [Systran/faster-whisper](https://github.com/SYSTRAN/faster-whisper) & [Hugging Face Hub (Systran/faster-whisper-tiny)](https://huggingface.co/Systran/faster-whisper-tiny)
- **License**: MIT License
- **Model Version**: `1.2.1` (using CTranslate2 backend v`4.8.1`)
- **Purpose**: Fast, lightweight automatic speech recognition (ASR) to convert raw voice streams into structured text transcripts with word/segment timestamps.
- **Input Specifications**:
  - Raw audio file or stream (WAV, FLAC, MP3, OGG, PCM).
  - Internal decoding handled via PyAV (`av` v18.1.0).
- **Output Specifications**:
  - `text`: Full concatenated transcript string.
  - `language`: Detected ISO language code (e.g. `en`).
  - `duration`: Audio length in seconds.
  - `segments`: List of segment objects with `start` time, `end` time, and segment `text`.
- **Execution Profile**:
  - Quantization: `int8`
  - Compute Device: CPU (`12 logical cores`)
  - Real-Time Factor (RTF): `~0.31` (1.0s audio transcribed in ~308ms)
- **Known Limitations**:
  - Short acoustic utterances or extreme background noise may cause transcription errors or omission of words.
  - `tiny` model trades a small fraction of accuracy for high throughput and low CPU resource consumption.

---

## 2. AASIST-L (Voice Anti-Spoofing Detection)

- **Model Name**: AASIST-L (Audio Anti-Spoofing using Integrated Spectro-Temporal Graph Attention Networks - Lightweight Variant)
- **Source Repository**: [SpeechAntiSpoofingBenchmarks/AASIST-L](https://huggingface.co/SpeechAntiSpoofingBenchmarks/AASIST-L)
- **License**: MIT License (Copyright (c) 2021-present NAVER Corp.)
- **Model Parameters**: 85,306 parameters (FP32)
- **Paper Citation**: Jung et al., *"AASIST: Audio Anti-Spoofing Using Integrated Spectro-Temporal Graph Attention Networks"*, ICASSP 2022.
- **Purpose**: Extracts raw acoustic anti-spoofing feature representations to distinguish genuine human voices from synthetic or voice-converted audio clips.
- **Input Specifications**:
  - Single-channel (mono) PCM audio sampled at `16,000 Hz`.
  - Deterministic evaluation window of exactly `64,600` samples (~4.0375 seconds).
  - Short audio is tile-padded; long audio is trimmed to the first 64,600 samples.
- **Output Specifications**:
  - `bona_fide_score`: Raw model logit index 1 (higher value = higher confidence of genuine human speech).
  - `synthetic_score`: Softmax probability for spoof/synthetic class (0.0 to 1.0) labelled as **VOICE AUTHENTICITY SIGNAL**.
  - `quality`: Signal quality assessment (`good` or `acceptable`).
  - `status`: `available` or `insufficient_evidence` (if < 0.5s or silent).
- **Known Limitations & Disclaimer**:
  > [!IMPORTANT]
  > **AASIST-L is a specialized voice anti-spoofing model, NOT a universal deepfake detector.**
  > - Its published performance is significantly stronger on in-domain ASVspoof2019 datasets (EER ~0.99%) than on out-of-domain real-world "InTheWild" dataset benchmarks (EER ~44.45%).
  > - Therefore, TrustShield **does not** treat AASIST-L as a standalone scam detector or final verdict.
  > - AASIST-L provides a **voice anti-spoofing signal** that TrustShield fuses with intent analysis, temporal context, and manipulation metrics in downstream risk engine layers.

# TrustShield AI Backend - Phase 7 Existing AASIST-L Voice Authenticity Integration

## 1. Existing AASIST-L Voice Authenticity Implementation
The source of truth for voice anti-spoofing in TrustShield AI is located at:
`D:\TrustShield\ai\voice_authenticity\voice_authenticity_service.py`

Key discovery findings:
- **Module**: `ai.voice_authenticity.voice_authenticity_service`
- **Main Function**: `analyze_audio(audio_path: str) -> Dict[str, Any]`
- **Model Source**: Hugging Face repository `SpeechAntiSpoofingBenchmarks/AASIST-L` (`AASIST-L.pth`)
- **Device & Acceleration**: PyTorch running on CPU (`map_location="cpu"`).
- **Model Warmth**: Cached in `_aasist_model_cache` module-level variable via `get_aasist_model()`.

## 2. Adapter Architecture
```text
 [ Client / WebSocket ]
           |
           v
 [ WS /api/v1/sessions/{id}/stream ]
           |
   (1) Receive binary chunk -> AudioBufferService
   (2) Decode audio         -> AudioDecoderService (16 kHz Mono PCM)
   (3) Independent Parallel Inference (asyncio.to_thread):
           +---------------------------------+---------------------------------+
           |                                                                   |
           v                                                                   v
 [ AITranscriptionAdapter ]                                     [ AIVoiceAuthenticityAdapter ]
           |                                                                   |
           v                                                                   v
 D:\TrustShield\ai\transcription                                 D:\TrustShield\ai\voice_authenticity
           |                                                                   |
           v                                                                   v
 TRANSCRIPT_PARTIAL / TRANSCRIPT_FINAL                            VOICE_ANALYSIS
```

The backend adapter (`app/ai_adapter/voice_authenticity.py`) creates a thin wrapper around `analyze_audio` without duplicating AASIST-L architecture, PyTorch models, or checkpoint loading.

## 3. AI Root Configuration
Configured centrally via `settings.TRUSTSHIELD_AI_ROOT` (default: `D:\TrustShield\ai`).
`app/ai_adapter/__init__.py` dynamically bootstraps `sys.path` so the AI package is importable without hardcoding absolute paths in backend logic.

## 4. Minimum Audio Requirement & Audio Quality Gating
- **Minimum Useful Duration**: 8,000 samples (0.5 seconds at 16 kHz Mono 16-bit PCM).
- **Short Chunks (< 0.5s)**: Handled safely by returning `{"status": "insufficient_evidence", "reason": "audio_too_short"}` without calling model inference or fabricating fake scores.
- **Audio Quality Gating**: `analyze_audio` performs RMS energy checks (`rms < 0.001` $\to$ `silence_or_low_energy`) and spectral flatness checks (`spectral_flatness > 0.85` $\to$ `unusable_audio`).

## 5. Score Semantics & Critical Rules
- **`synthetic_score`**: Softmax probability of synthetic/spoofed voice (`probs[0, 0]`) in range `[0.0, 1.0]`. Higher score = synthetic/fake; lower score = genuine.
- **`bona_fide_score`**: Logit score for genuine class (`logits[0, 1]`).
- **`bona_fide_probability`**: Softmax probability of genuine class (`probs[0, 1]`).
- **Critical Semantic Rule**: `synthetic_score` is strictly a **Voice Authenticity Signal**. It is **never** renamed or reinterpreted as a scam probability, financial fraud probability, or caller intent.

## 6. Event Protocol

### `VOICE_ANALYSIS` Event (Available)
```json
{
  "type": "VOICE_ANALYSIS",
  "version": 1,
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": "2026-08-29T12:00:00.000000+00:00",
  "payload": {
    "status": "available",
    "synthetic_score": 0.18,
    "bona_fide_score": 2.14,
    "bona_fide_probability": 0.82,
    "quality": "good",
    "rms_energy": 0.05,
    "spectral_flatness": 0.12,
    "input_duration_sec": 1.0
  }
}
```

### `VOICE_ANALYSIS` Event (Insufficient Evidence)
```json
{
  "type": "VOICE_ANALYSIS",
  "version": 1,
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": "2026-08-29T12:00:00.000000+00:00",
  "payload": {
    "status": "insufficient_evidence",
    "reason": "audio_too_short",
    "samples": 4800,
    "duration_sec": 0.3
  }
}
```

## 7. Health Readiness
`GET /health` reports readiness status for both AI services:
```json
{
  "status": "ok",
  "service": "trustshield-backend",
  "version": "0.1.0",
  "phase": 1,
  "ai_readiness": {
    "transcription": "READY",
    "voice_authenticity": "READY"
  }
}
```

## 8. Privacy & Security
- Audio files used for AASIST input are created in system temp storage and deleted immediately after inference.
- Zero raw audio content is included in WebSocket JSON event payloads or logs.

## 9. Current Limitations
- Synthetic test tones (e.g. 440 Hz sine waves) verify pipeline execution and model inference, but do not represent accuracy benchmarks.
- Conversation intelligence, intent detection, and risk scoring belong to future phases.

## 10. Next Phase
- **Phase 8**: Conversation intelligence + structured signal extraction.

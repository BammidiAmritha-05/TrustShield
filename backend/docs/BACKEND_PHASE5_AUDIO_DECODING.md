# TrustShield AI Backend - Phase 5 Audio Decoding & Format Validation

## 1. Architecture
Phase 5 implements an in-memory **Audio Decoder Service** (`app/services/audio_decoder_service.py`) integrated into the WebSocket streaming pipeline (`WS /api/v1/sessions/{session_id}/stream`).

It converts incoming browser audio streams into a normalized, predictable internal representation suitable for future AI processing, validates audio technical metrics (sample rate, channel count, sample count, duration), and emits `AUDIO_DECODED` metadata events.

Phase 5 remains strictly standalone without executing AI models (`faster-whisper`, `AASIST`).

## 2. Decoder Choice & Library Rationale
- **Primary Decoding Engine**: `soundfile` (`libsndfile` backend) + standard library `wave` + `scipy.signal`.
- **Rationale**:
  - `soundfile 0.13.1` and `scipy 1.16.3` are already installed and verified in the Python 3.13 Windows environment.
  - Native in-memory decoding of WAV, OGG (Opus/Vorbis), FLAC, and AIFF containers via `io.BytesIO`.
  - Zero disk write overhead and no external executable subprocess dependencies.

## 3. Supported Input Formats
- **WAV** (Uncompressed PCM, 8/16/24/32-bit, mono/stereo)
- **OGG** (Opus / Vorbis container streams)
- **FLAC**
- **AIFF**

## 4. Normalized Output Format
Successfully decoded audio is normalized to match TrustShield AI pipeline expectations:
- **Sample Rate**: `16,000 Hz` (16 kHz)
- **Channels**: `1` (Mono) — Stereo audio is averaged across channels (`audio.mean(axis=1)`).
- **Sample Width**: `2 bytes` (16-bit signed PCM, `pcm_s16le`).
- **Resampling**: `scipy.signal.resample` resamples inputs with non-16kHz rates.

## 5. Decoded Audio Metadata & Schema

### `AUDIO_DECODED` Event
Emitted over WebSocket immediately after successful decoding:
```json
{
  "type": "AUDIO_DECODED",
  "version": 1,
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": "2026-08-29T12:29:35.506726+00:00",
  "payload": {
    "sample_rate": 16000,
    "channels": 1,
    "sample_width": 2,
    "sample_count": 8000,
    "duration_seconds": 0.5,
    "format": "pcm_s16le",
    "codec": "pcm_s16le"
  }
}
```

## 6. Limits & Validation Rules
- **Maximum Audio Duration**: `MAX_AUDIO_DURATION_SECONDS` = `300.0` seconds (5 minutes max per audio segment).
- **Validation**:
  - Non-empty byte payload (`EMPTY_AUDIO`).
  - Container header recognition (`UNSUPPORTED_AUDIO_FORMAT`).
  - Signal sample count > 0 & duration > 0 (`AUDIO_DURATION_INVALID`).
  - Duration $\le$ 300s (`AUDIO_DURATION_TOO_LONG`).

## 7. Streaming Container Considerations
- Browser `MediaRecorder` chunks may contain fragmented container headers (e.g., initial WebM/OGG header in chunk 0, raw cluster data in subsequent chunks).
- Full session buffers are accumulated in `AudioBufferService` prior to container decoding. Incomplete header chunks trigger structured `AUDIO_DECODE_FAILED` / `UNSUPPORTED_AUDIO_FORMAT` errors without dropping the socket.

## 8. Privacy & Security
- **Temporary Memory Processing**: Raw PCM bytes are stored strictly in memory inside `DecodedAudio` during processing.
- **Zero Raw Expose**: Raw PCM bytes are **never** included in WebSocket JSON events, REST API payloads, or log files.
- **Zero Disk Persistence**: No audio files are created on disk.

## 9. Cleanup
Ending a session (`stop` command or REST `POST /end`) purges both the raw `AudioBufferService` bytearray and temporary `DecodedAudio` memory.

## 10. AI Integration Requirements Discovered
Inspection of `D:\TrustShield\ai` (`transcription/transcription_service.py` & `voice_authenticity/voice_authenticity_service.py`) confirms:
1. `faster-whisper` expects audio input path or 16 kHz Mono audio float/int PCM arrays.
2. `AASIST-L` voice authenticity model expects **16 kHz Mono float32** NumPy arrays (`_CUT = 64600` samples).
3. The normalized 16 kHz mono output created in Phase 5 directly fulfills these exact AI pipeline requirements.

## 11. Current Limitations
- No AI model inference (Whisper transcription or AASIST voice authenticity) is executed in Phase 5.

## 12. Next Phase
- **Phase 6**: Whisper / faster-whisper integration.

# TrustShield AI Backend - Phase 4 Safe Temporary Audio Buffer & Input Validation

## 1. Architecture
Phase 4 implements a safe, in-memory **Audio Buffer Service** (`app/services/audio_buffer_service.py`) integrated into the WebSocket streaming pipeline (`WS /api/v1/sessions/{session_id}/stream`).

It validates incoming binary frames, appends them to temporary in-memory byte buffers (`bytearray`) isolated per session, tracks safe chunk metadata, emits standardized `AUDIO_BUFFERED` events, enforces strict chunk and total session memory limits, and purges buffers when sessions terminate.

Phase 4 remains strictly standalone without audio decoding (FFmpeg) or AI model inference.

## 2. Buffer Lifecycle
```text
 [ Client ]                                       [ Server / AudioBufferService ]
     |                                                          |
     | ---- Binary Frame (bytes) -----------------------------> |
     |                                                          | (Validate size & memory limits)
     |                                                          | (Append bytes to in-memory bytearray)
     | <--- EVENT: AUDIO_BUFFERED ----------------------------  |
     |      {"bytes": 1024, "total_buffered_bytes": 1024,      |
     |       "chunk_count": 1}                                  |
     |                                                          |
     | ---- Text JSON: {"action": "stop"} --------------------> |
     |                                                          | (audio_buffer_service.clear_buffer)
     | <--- EVENT: SESSION_ENDED ------------------------------ | (Session status -> ended)
```

## 3. Validation Rules
- **Binary Existence**: Every binary frame must contain bytes (`len(data) > 0`). Empty binary frames are rejected (`code="EMPTY_AUDIO_CHUNK"`).
- **Chunk Size Limit**: Single binary frame size must not exceed `MAX_AUDIO_CHUNK_BYTES`. Oversized chunks are rejected (`code="AUDIO_CHUNK_TOO_LARGE"`).
- **Total Session Memory Limit**: Accumulated session buffer size must not exceed `MAX_SESSION_AUDIO_BYTES`. Exceeding chunks are rejected (`code="SESSION_AUDIO_LIMIT_EXCEEDED"`).
- **Format Agnostic**: No audio codec assumptions (WAV/PCM/WebM/Opus) are made in Phase 4. Binary payloads are treated strictly as opaque bytes.

## 4. Memory Limits & Configuration
Configured in `app/config.py`:
- `MAX_AUDIO_CHUNK_BYTES`: `1,048,576` bytes (1 MB default max chunk size).
- `MAX_SESSION_AUDIO_BYTES`: `10,485,760` bytes (10 MB default max session buffer size).

## 5. Privacy & Security
- **In-Memory Only**: Audio data is held strictly in memory (`bytearray`) during active session processing.
- **Zero Disk Persistence**: Raw audio bytes are **never** written to disk files or permanent log stores.
- **No Raw Logging**: Raw audio content is excluded from log messages and JSON response payloads.
- **Metadata Only**: Only non-sensitive operational metadata is tracked (`chunk_count`, `total_bytes`, timestamps).

## 6. WebSocket Event Specification

### `AUDIO_BUFFERED` Event
Emitted immediately upon successfully validating and appending a binary chunk:
```json
{
  "type": "AUDIO_BUFFERED",
  "version": 1,
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": "2026-08-29T12:29:35.506726+00:00",
  "payload": {
    "bytes": 1024,
    "total_buffered_bytes": 2048,
    "chunk_count": 2
  }
}
```

## 7. Stop Cleanup
When a session is ended via WebSocket `{"action": "stop"}` or REST `POST /api/v1/sessions/{id}/end`:
1. `session_service.end_session` marks the session status as `ended`.
2. `audio_buffer_service.clear_buffer(session_id)` is invoked, immediately purging all buffered raw bytes and metadata for that session from memory.

## 8. Disconnect Behavior
- A WebSocket client disconnect does **not** automatically destroy the session or purge its audio buffer, allowing seamless client reconnection.
- Audio buffers are destroyed only when the session is explicitly ended (`stop` command or REST `POST /end`).

## 9. Current Limitations
- Raw binary bytes are accumulated without decoding or audio sample rate conversion.
- No AI model inference (Whisper transcription or AASIST voice authenticity) is connected in Phase 4.

## 10. Next Phase
- **Phase 5**: Audio decoding + format validation foundation.

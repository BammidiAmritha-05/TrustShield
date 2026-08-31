# TrustShield AI Backend - Phase 3 WebSocket Foundation

## 1. Architecture
Phase 3 establishes a lightweight, reliable WebSocket foundation endpoint:
`WS /api/v1/sessions/{session_id}/stream`

This endpoint connects a client to an existing protection session created in Phase 2. It handles session validation, consent checks, structured text commands, opaque binary frames, payload size limiting, standardized event serialization, and clean disconnects without introducing AI pipeline dependencies or database requirements.

## 2. WebSocket Lifecycle
```text
 [ Client ]                                              [ FastAPI Server ]
     |                                                          |
     | ---- WS /api/v1/sessions/{session_id}/stream ----------> |
     |                                                          | (Verify session & consent)
     | <--- ACCEPT CONNECTION --------------------------------- | (Transition status -> active)
     | <--- EVENT: SESSION_STARTED ---------------------------- |
     |                                                          |
     | ---- Text JSON: {"action": "send_text", "text": "..."}-> |
     | <--- EVENT: TEXT_RECEIVED ------------------------------ |
     |                                                          |
     | ---- Binary Frame: <raw bytes> ------------------------> |
     | <--- EVENT: BINARY_RECEIVED {"bytes": <len>} ----------- |
     |                                                          |
     | ---- Text JSON: {"action": "stop"} --------------------> | (session_service.end_session)
     | <--- EVENT: SESSION_ENDED ------------------------------ |
     | <--- CLOSE SOCKET (1000) ------------------------------- |
```

## 3. Session Validation
Prior to calling `websocket.accept()`, the connection request undergoes three strict pre-handshake checks:
1. **Existence**: Session ID must exist in session storage. (Missing session -> close socket with code `4004`).
2. **Consent**: Session `consent` must equal `true`. (Missing consent -> close socket with code `4003`).
3. **Status**: Session must NOT be in `ended` state. (Ended session -> close socket with code `4003`).

If session status is `created`, calling `websocket.accept()` automatically transitions the session status to `active`.

## 4. Message Protocol (Client -> Server)

### 4.1 Text Commands (JSON)
- **Send Text**:
```json
{
  "action": "send_text",
  "text": "Suspicious caller claims to be from IT department."
}
```
- **Stop Session**:
```json
{
  "action": "stop"
}
```

### 4.2 Binary Messages (Opaque Frames)
- Raw binary WebSocket frames (bytes) representing opaque data streams.

## 5. Event Protocol (Server -> Client)
All server events adhere to a strict versioned JSON schema:

```json
{
  "type": "SESSION_STARTED | TEXT_RECEIVED | BINARY_RECEIVED | ERROR | SESSION_ENDED",
  "version": 1,
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": "2026-08-29T12:00:00.000000Z",
  "payload": {}
}
```

### Event Specifications:
- `SESSION_STARTED`: Emitted immediately upon connection accept. `payload = {"status": "active"}`.
- `TEXT_RECEIVED`: Emitted upon valid text command. `payload = {"text": "..."}`.
- `BINARY_RECEIVED`: Emitted upon valid binary frame. `payload = {"bytes": <byte_count>}`.
- `ERROR`: Emitted when payload fails validation. `payload = {"code": "...", "message": "..."}`.
- `SESSION_ENDED`: Emitted when client sends `stop`. `payload = {"status": "ended", "ended_at": "..."}`.

## 6. Binary Payload Handling
- Binary frames are validated only for non-emptiness and size.
- Binary data is treated purely as an opaque byte payload in Phase 3 (no audio decoding, FFmpeg, or AI processing).
- **Security Rule**: Raw binary data is NEVER included in JSON events or stored in memory/logs.

## 7. Limits & Configuration
Configured in `app/config.py`:
- `MAX_WS_MESSAGE_BYTES`: `1,048,576` bytes (1 MB) max payload size.
- `MAX_WS_TEXT_LENGTH`: `10,000` characters max text message length.

## 8. Error Handling
Invalid messages return a structured `ERROR` event without dropping the WebSocket connection unless requested by the client or unrecoverable:
- Malformed JSON -> `ERROR` (code: `MALFORMED_JSON`)
- Unsupported Action -> `ERROR` (code: `UNSUPPORTED_ACTION`)
- Empty Text -> `ERROR` (code: `INVALID_TEXT`)
- Oversized Text/Binary Payload -> `ERROR` (code: `OVERSIZED_PAYLOAD`)

## 9. Disconnect Behavior
- Client disconnections (`WebSocketDisconnect`) are caught gracefully.
- A disconnect does **not** automatically mark the session as `ended`. The session remains `active`, enabling seamless client reconnection.
- Session termination requires sending `{"action": "stop"}` or calling `POST /api/v1/sessions/{id}/end`.

## 10. Privacy & Security
- Strict consent verification prior to connection acceptance.
- Raw binary payloads and text contents are not logged or persisted to disk. Only event metadata counts are tracked.

## 11. Current Limitations
- No real-time AI transcription (Whisper), voice authenticity (AASIST), or risk evaluation is active in Phase 3.

## 12. Next Phase
- **Phase 4**: Audio buffer + input validation foundation.

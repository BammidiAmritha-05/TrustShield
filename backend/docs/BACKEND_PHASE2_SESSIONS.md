# TrustShield AI Backend - Phase 2 Protection Session API

## 1. Purpose
This document details the design, architecture, endpoints, and verification for **Phase 2: Protection Session API** of the TrustShield AI backend service.

Phase 2 establishes session lifecycle management, user consent enforcement, request validation, and an isolated in-memory storage abstraction layer.

## 2. Session Lifecycle
A protection session represents a user's active monitoring window:
1. **Creation**: `POST /api/v1/sessions` creates a session with `status = "created"`, `consent = true`, and a UTC timestamp.
2. **Retrieval**: `GET /api/v1/sessions/{session_id}` returns the current status and metadata.
3. **Termination**: `POST /api/v1/sessions/{session_id}/end` transitions the status to `"ended"` and records `ended_at`.
4. **History**: `GET /api/v1/sessions` lists past sessions ordered newest first.

```
 [ Client ] ---> POST /api/v1/sessions ---> Status: created
    |
    +---------> GET  /api/v1/sessions/{id} ---> Status: created / active / ended
    |
    +---------> POST /api/v1/sessions/{id}/end ---> Status: ended (ended_at set)
    |
    +---------> GET  /api/v1/sessions ---> List[SessionResponse] (Newest first)
```

## 3. Session Schema
```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "created",
  "interaction_type": "voice",
  "consent": true,
  "created_at": "2026-08-29T17:55:00+00:00",
  "ended_at": null
}
```

### Fields:
- `session_id` (`string`, UUID v4): Unique session identifier.
- `status` (`string`): Enum (`created`, `active`, `ended`).
- `interaction_type` (`string`): Enum (`voice`, `text`, `demo`).
- `consent` (`boolean`): Explicit user consent (`true` required).
- `created_at` (`datetime`): UTC timestamp when session was initialized.
- `ended_at` (`datetime` | `null`): UTC timestamp when session ended (`null` while active).

## 4. API Endpoints

### 4.1 Create Session
- **POST** `/api/v1/sessions`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "interaction_type": "voice",
  "consent": true
}
```
- **Response**: `HTTP 201 Created` with full session schema.

### 4.2 Retrieve Session
- **GET** `/api/v1/sessions/{session_id}`
- **Response**: `HTTP 200 OK` with session details.
- **Error**: `HTTP 404 Not Found` if session ID does not exist.

### 4.3 End Session
- **POST** `/api/v1/sessions/{session_id}/end`
- **Response**: `HTTP 200 OK` with updated session (`status = "ended"`).
- **Error**: `HTTP 400 Bad Request` if session is already ended.

### 4.4 List Session History
- **GET** `/api/v1/sessions`
- **Response**: `HTTP 200 OK` returning JSON array of session objects (newest first).

## 5. Validation Rules
- `interaction_type` must strictly match one of: `"voice"`, `"text"`, `"demo"`. Unsupported types return `HTTP 422 Unprocessable Entity`.
- `consent` must explicitly equal `true`. Omitting `consent` or passing `false` returns `HTTP 422`.
- Extra unknown JSON fields in create requests are forbidden (`extra = "forbid"`).

## 6. Storage Abstraction
The `InMemorySessionStore` (`app/storage/session_store.py`) decouples API handlers from data persistence:
- Encapsulates dictionary storage behind thread-safe methods (`create`, `get`, `update`, `list`).
- Ensures future migration to SQLite or PostgreSQL will require zero changes to `app/api/sessions.py` or `SessionService`.

## 7. Error Handling
- Invalid JSON or validation failures: `HTTP 422 Unprocessable Entity` (FastAPI standard JSON format).
- Non-existent session lookup/end: `HTTP 404 Not Found`.
- Re-ending an already ended session: `HTTP 400 Bad Request`.
- Internal server errors: Clean `HTTP 500` JSON response without exposing Python stack traces.

## 8. Privacy Considerations
- Sessions require explicit user consent (`consent=true`) prior to creation.
- No personal user identifiable information (PII) or raw interaction payloads are stored in the session record.

## 9. Limitations
- Session storage is in-memory only in Phase 2; state resets upon server restart.
- No real-time WebSockets or AI streaming engines are attached in this phase.

## 10. Next Phase
- **Phase 3**: WebSocket Foundation (Real-time connection handshake, frame protocol, and streaming channels).

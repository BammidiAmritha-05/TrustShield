# TrustShield AI Backend - Phase 1 Foundation

## 1. Purpose
This document specifies the architecture, setup, configuration, and verification details for **Phase 1: Clean FastAPI Backend Foundation** of the TrustShield AI standalone backend system.

TrustShield AI is a human-centric AI safety copilot that helps users understand suspicious interactions and verify risky claims before taking dangerous actions. Phase 1 provides a clean, robust, standalone FastAPI application foundation.

## 2. Standalone Location
- **Primary Development Location**: `D:\backend`
- **Workspace Link**: `D:\Bakend TrustShield` (junctioned directly to `D:\backend`)
- **Isolation**: Completely decoupled from external frontend repositories or monolithic directories (`D:\TrustShield`). No hardcoded paths to `D:\TrustShield` exist in source code.

## 3. Project Structure
```text
D:\backend
│
├── app
│   ├── __init__.py      # App package initializer
│   ├── config.py        # Environment-based Pydantic configuration
│   └── main.py          # FastAPI application & health endpoint
│
├── tests
│   └── test_health.py   # Automated pytest suite for /health endpoint
│
├── docs
│   └── BACKEND_PHASE1_FOUNDATION.md # Technical documentation
│
├── .env.example         # Environment variable template
├── .env                 # Environment configuration file
├── requirements.txt     # Phase 1 minimal python dependencies
└── README.md            # Quickstart guide
```

## 4. Python Version
- **Runtime Environment**: Python `3.13.7` (64-bit Windows)

## 5. Dependencies
The Phase 1 foundation uses only lightweight, essential dependencies:
- `fastapi` (`>=0.115.0`) - Web framework
- `uvicorn[standard]` (`>=0.30.0`) - ASGI web server
- `pydantic` (`>=2.0.0`) - Data validation
- `pydantic-settings` (`>=2.0.0`) - Environment settings management
- `python-dotenv` (`>=1.0.0`) - Environment file loader
- `pytest` (`>=8.0.0`) - Automated testing framework
- `httpx` (`>=0.27.0`) - Async HTTP client for test suite

## 6. Startup Command
Start the development server using uvicorn:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 7. Health Endpoint
- **HTTP Route**: `GET /health`
- **HTTP Response Code**: `200 OK`
- **Response Format**:
```json
{
  "status": "ok",
  "service": "trustshield-backend",
  "version": "0.1.0",
  "phase": 1
}
```

## 8. Environment Variables
Supported environment settings in `app/config.py`:
- `APP_ENV`: Application environment (`development`, `staging`, `production`). Default: `development`
- `HOST`: Bind host address. Default: `127.0.0.1`
- `PORT`: Bind port number. Default: `8000`
- `LOG_LEVEL`: Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Default: `INFO`
- `TRUSTSHIELD_AI_ROOT`: Path to external AI system (Optional in Phase 1). Default: `""`
- `CORS_ORIGINS`: Configurable allowed origins list. Default: `["http://localhost:3000", "http://127.0.0.1:3000"]`

## 9. Current Limitations
- AI models (transcription, voice authenticity, conversation intelligence, risk engine) are **not** loaded or reported as ready in Phase 1.
- No session management or state persistence is implemented yet.
- No WebSockets or real-time streaming channels are active in Phase 1.
- Authentication and database connections are deferred to later phases.

## 10. Next Phase
- **Phase 2**: Session API (Session lifecycle management, state initialization, and structured request handlers).

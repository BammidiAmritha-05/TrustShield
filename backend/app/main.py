import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai_adapter.claim import default_claim_adapter
from app.ai_adapter.conversation import default_conversation_adapter
from app.ai_adapter.protection import default_protection_adapter
from app.ai_adapter.risk import default_risk_adapter
from app.ai_adapter.transcription import default_transcription_adapter
from app.ai_adapter.voice_authenticity import default_voice_authenticity_adapter
from app.api.sessions import router as sessions_router
from app.api.websocket import router as websocket_router
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("trustshield-backend")

app = FastAPI(
    title="TrustShield AI Backend",
    version="0.1.0",
    description="Human-centric AI safety copilot backend service"
)

# Configurable CORS
if settings.CORS_ORIGINS:
    cors_origins = (
        settings.CORS_ORIGINS
        if isinstance(settings.CORS_ORIGINS, list)
        else [settings.CORS_ORIGINS]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
        }
    )


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "ok",
        "service": "trustshield-backend",
        "version": app.version,
        "phase": 1,
        "ai_readiness": {
            "transcription": default_transcription_adapter.get_readiness_status(),
            "voice_authenticity": default_voice_authenticity_adapter.get_readiness_status(),
            "conversation_intelligence": default_conversation_adapter.get_readiness_status(),
            "risk_engine": default_risk_adapter.get_readiness_status(),
            "protection_agent": default_protection_adapter.get_readiness_status(),
            "claim_verification": default_claim_adapter.get_readiness_status()
        }
    }


# Register Routers
app.include_router(sessions_router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(websocket_router, prefix="/api/v1/sessions", tags=["websocket"])

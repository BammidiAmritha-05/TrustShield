from typing import List
from fastapi import APIRouter, Depends, status

from app.models import SessionCreateRequest, SessionResponse
from app.services.session_service import SessionService, default_session_service

router = APIRouter()


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new protection session",
    description="Creates a new TrustShield protection session requiring explicit consent."
)
async def create_session(
    request: SessionCreateRequest,
    service: SessionService = Depends(lambda: default_session_service)
) -> SessionResponse:
    return service.create_session(request)


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve session details",
    description="Retrieves current state and metadata for an existing protection session."
)
async def get_session(
    session_id: str,
    service: SessionService = Depends(lambda: default_session_service)
) -> SessionResponse:
    return service.get_session(session_id)


@router.post(
    "/{session_id}/end",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="End an active protection session",
    description="Ends an existing protection session and records the ended_at timestamp."
)
async def end_session(
    session_id: str,
    service: SessionService = Depends(lambda: default_session_service)
) -> SessionResponse:
    return service.end_session(session_id)


@router.get(
    "",
    response_model=List[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List protection session history",
    description="Lists all protection sessions in memory, ordered newest first."
)
async def list_sessions(
    service: SessionService = Depends(lambda: default_session_service)
) -> List[SessionResponse]:
    return service.list_sessions()

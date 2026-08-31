from datetime import datetime, timezone
from typing import List
from uuid import uuid4
from fastapi import HTTPException, status

from app.models import EventMetadata, InteractionType, SessionCreateRequest, SessionResponse, SessionStatus
from app.services.audio_buffer_service import default_audio_buffer_service
from app.services.evidence_store import default_evidence_store
from app.storage.session_store import InMemorySessionStore, session_store


class SessionService:
    def __init__(self, store: InMemorySessionStore = session_store):
        self.store = store

    def create_session(self, request: SessionCreateRequest) -> SessionResponse:
        session = SessionResponse(
            session_id=str(uuid4()),
            status=SessionStatus.CREATED,
            interaction_type=request.interaction_type,
            consent=request.consent,
            created_at=datetime.now(timezone.utc),
            ended_at=None,
            event_count=0
        )
        return self.store.create(session)

    def get_session(self, session_id: str) -> SessionResponse:
        session = self.store.get(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID '{session_id}' not found."
            )
        return session

    def activate_session(self, session_id: str) -> SessionResponse:
        session = self.get_session(session_id)
        if session.status == SessionStatus.CREATED:
            session.status = SessionStatus.ACTIVE
            return self.store.update(session)
        return session

    def end_session(self, session_id: str) -> SessionResponse:
        session = self.get_session(session_id)
        if session.status == SessionStatus.ENDED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Session '{session_id}' is already ended."
            )
        
        session.status = SessionStatus.ENDED
        session.ended_at = datetime.now(timezone.utc)
        
        # Purge temporary audio buffer and evidence store upon session termination
        default_audio_buffer_service.clear_buffer(session_id)
        default_evidence_store.clear_session(session_id)

        return self.store.update(session)

    def record_event_metadata(self, session_id: str, event_type: str, details: dict) -> None:
        event = EventMetadata(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            details=details
        )
        self.store.record_event(session_id, event)

    def list_sessions(self) -> List[SessionResponse]:
        return self.store.list()


# Global service instance
default_session_service = SessionService()

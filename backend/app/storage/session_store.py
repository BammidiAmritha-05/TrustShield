import threading
from typing import Dict, List, Optional
from app.models import EventMetadata, SessionResponse


class InMemorySessionStore:
    """
    Thread-safe in-memory session store abstraction.
    Allows easy swapping to persistent database (SQLite / PostgreSQL) in later phases.
    """

    def __init__(self):
        self._sessions: Dict[str, SessionResponse] = {}
        self._event_logs: Dict[str, List[EventMetadata]] = {}
        self._lock = threading.Lock()

    def create(self, session: SessionResponse) -> SessionResponse:
        with self._lock:
            self._sessions[session.session_id] = session.model_copy()
            self._event_logs[session.session_id] = []
            return session.model_copy()

    def get(self, session_id: str) -> Optional[SessionResponse]:
        with self._lock:
            session = self._sessions.get(session_id)
            return session.model_copy() if session else None

    def update(self, session: SessionResponse) -> SessionResponse:
        with self._lock:
            if session.session_id not in self._sessions:
                raise KeyError(f"Session {session.session_id} not found in store.")
            self._sessions[session.session_id] = session.model_copy()
            return session.model_copy()

    def record_event(self, session_id: str, event: EventMetadata) -> None:
        """Record event metadata (e.g. byte count, event type) - never raw binary."""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].event_count += 1
                if session_id in self._event_logs:
                    self._event_logs[session_id].append(event)

    def list(self) -> List[SessionResponse]:
        with self._lock:
            sessions = [s.model_copy() for s in self._sessions.values()]
            return sorted(sessions, key=lambda s: s.created_at, reverse=True)

    def clear(self) -> None:
        """Utility for test suite reset."""
        with self._lock:
            self._sessions.clear()
            self._event_logs.clear()


# Global store instance
session_store = InMemorySessionStore()

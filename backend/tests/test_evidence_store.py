import pytest
from app.services.evidence_store import SessionEvidenceStore, MAX_EVIDENCE_RECORDS_PER_SESSION


def test_evidence_store_instantiation_and_isolation():
    """Verify session isolation in SessionEvidenceStore."""
    store = SessionEvidenceStore()
    engine1 = store.get_or_create_engine("session-1")
    engine2 = store.get_or_create_engine("session-2")

    assert engine1 is not engine2
    assert store.get_turn_index("session-1") == 1
    assert store.get_turn_index("session-2") == 1


def test_advance_turn_index():
    """Verify turn index advancement."""
    store = SessionEvidenceStore()
    assert store.get_turn_index("session-1") == 1
    new_idx = store.advance_turn_index("session-1")
    assert new_idx == 2
    assert store.get_turn_index("session-1") == 2


def test_bounded_memory_limit():
    """Verify evidence history does not exceed MAX_EVIDENCE_RECORDS_PER_SESSION (50)."""
    store = SessionEvidenceStore()
    engine = store.get_or_create_engine("session-1")

    from ai.evidence.evidence_schema import NormalizedEvidence, EvidenceSource

    # Add 60 evidence items
    for i in range(60):
        item = NormalizedEvidence(
            signal=f"signal_{i}",
            value=f"value_{i}",
            confidence=0.9,
            source=EvidenceSource.INTENT.value,
            turn_index=i
        )
        engine.accumulator.add_evidence(item)

    # Call get_or_create_engine to trigger memory bounding
    bounded_engine = store.get_or_create_engine("session-1")
    assert len(bounded_engine.accumulator.evidence_history) == MAX_EVIDENCE_RECORDS_PER_SESSION
    assert bounded_engine.accumulator.evidence_history[-1].signal == "signal_59"


def test_clear_session_and_clear_all():
    """Verify session cleanup and clear_all methods."""
    store = SessionEvidenceStore()
    store.get_or_create_engine("session-1")
    store.get_or_create_engine("session-2")

    store.clear_session("session-1")
    assert "session-1" not in store._session_engines

    store.clear_all()
    assert len(store._session_engines) == 0

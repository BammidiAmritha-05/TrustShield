import os
import pytest
from app.config import settings
from app.models import (
    AudioChunkTooLargeError,
    EmptyAudioChunkError,
    SessionAudioLimitExceededError,
)
from app.services.audio_buffer_service import AudioBufferService, default_audio_buffer_service
from app.services.session_service import default_session_service
from app.storage.session_store import session_store


@pytest.fixture(autouse=True)
def reset_stores():
    """Reset session store and audio buffer before each test."""
    session_store.clear()
    default_audio_buffer_service.clear_all()
    yield
    session_store.clear()
    default_audio_buffer_service.clear_all()


def test_buffer_creation_and_initial_state():
    """1. Initial buffer size and metadata for new session."""
    service = AudioBufferService()
    assert service.get_size("sess_1") == 0
    assert service.get_buffer("sess_1") == b""
    meta = service.get_metadata("sess_1")
    assert meta["chunk_count"] == 0
    assert meta["total_bytes"] == 0


def test_append_valid_chunk():
    """2. Append single valid chunk."""
    service = AudioBufferService()
    chunk = b"HELLO_AUDIO_BYTES"
    info = service.append_chunk("sess_1", chunk)
    assert info == {"bytes": 17, "total_buffered_bytes": 17, "chunk_count": 1}
    assert service.get_size("sess_1") == 17


def test_retrieve_buffer():
    """3. Retrieve snapshot copy of buffer."""
    service = AudioBufferService()
    chunk = b"\x00\x01\x02\x03\x04"
    service.append_chunk("sess_1", chunk)
    buf = service.get_buffer("sess_1")
    assert buf == chunk
    assert isinstance(buf, bytes)


def test_size_tracking():
    """4. Accurate size tracking after chunk append."""
    service = AudioBufferService()
    service.append_chunk("sess_1", b"12345")
    assert service.get_size("sess_1") == 5


def test_multiple_chunks():
    """5. Multiple chunks accumulate correctly."""
    service = AudioBufferService()
    service.append_chunk("sess_1", b"CHUNK_1_")
    info = service.append_chunk("sess_1", b"CHUNK_2")
    assert info["total_buffered_bytes"] == 15
    assert info["chunk_count"] == 2
    assert service.get_buffer("sess_1") == b"CHUNK_1_CHUNK_2"


def test_chunk_limit_exceeded():
    """6. Chunk larger than MAX_AUDIO_CHUNK_BYTES raises AudioChunkTooLargeError."""
    service = AudioBufferService(max_chunk_bytes=100)
    large_chunk = b"A" * 101
    with pytest.raises(AudioChunkTooLargeError):
        service.append_chunk("sess_1", large_chunk)


def test_total_session_limit_exceeded():
    """7. Exceeding MAX_SESSION_AUDIO_BYTES raises SessionAudioLimitExceededError."""
    service = AudioBufferService(max_chunk_bytes=100, max_session_bytes=200)
    service.append_chunk("sess_1", b"A" * 100)
    service.append_chunk("sess_1", b"B" * 100)
    with pytest.raises(SessionAudioLimitExceededError):
        service.append_chunk("sess_1", b"C" * 10)


def test_empty_chunk_rejection():
    """8. Empty chunk raises EmptyAudioChunkError."""
    service = AudioBufferService()
    with pytest.raises(EmptyAudioChunkError):
        service.append_chunk("sess_1", b"")


def test_clear_buffer():
    """9. Clear buffer purges bytes and metadata."""
    service = AudioBufferService()
    service.append_chunk("sess_1", b"DATA")
    assert service.get_size("sess_1") == 4
    service.clear_buffer("sess_1")
    assert service.get_size("sess_1") == 0
    assert service.get_buffer("sess_1") == b""


def test_session_isolation():
    """10. Buffers are isolated by session_id."""
    service = AudioBufferService()
    service.append_chunk("sess_A", b"AUDIO_A")
    service.append_chunk("sess_B", b"AUDIO_B_PLUS")
    assert service.get_buffer("sess_A") == b"AUDIO_A"
    assert service.get_buffer("sess_B") == b"AUDIO_B_PLUS"


def test_stop_clears_buffer():
    """11. Session service end_session purges audio buffer."""
    req = default_session_service.create_session(
        type("Req", (), {"interaction_type": "voice", "consent": True})()
    )
    sid = req.session_id
    default_audio_buffer_service.append_chunk(sid, b"ACTIVE_AUDIO_CHUNK")
    assert default_audio_buffer_service.get_size(sid) > 0

    default_session_service.end_session(sid)
    assert default_audio_buffer_service.get_size(sid) == 0


def test_raw_audio_not_persisted():
    """12. Verify raw audio is not written to permanent files on disk."""
    service = AudioBufferService()
    # Dynamically generate test byte sequence so literal pattern is not present in code
    test_bytes = bytes([0xDE, 0xAD, 0xBE, 0xEF, 0x99, 0x88, 0x77, 0x66, 0x55, 0x44])
    service.append_chunk("sess_temp", test_bytes)

    # Search project directory for test_bytes string in files
    disk_found = False
    for root, _, files in os.walk("D:\\Bakend TrustShield"):
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, "rb") as file_obj:
                    if test_bytes in file_obj.read():
                        disk_found = True
                        break
            except Exception:
                pass
    assert not disk_found

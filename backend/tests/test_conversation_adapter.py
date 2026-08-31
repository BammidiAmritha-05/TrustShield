import pytest
from unittest.mock import patch, MagicMock

from app.ai_adapter.conversation import AIConversationAdapter
from app.config import settings
from app.models import (
    ConversationIntelligenceFailedError,
    ConversationIntelligenceUnavailableError,
)


def test_adapter_import():
    """1. Adapter import and instantiation."""
    adapter = AIConversationAdapter()
    assert adapter is not None


def test_ai_root_missing(monkeypatch):
    """2. AI root missing sets readiness status to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "")
    adapter = AIConversationAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"
    assert not adapter.is_available()


def test_ai_module_unavailable(monkeypatch):
    """3. Non-existent AI root directory sets readiness status to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "D:\\NonExistentPath\\ai")
    adapter = AIConversationAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"


def test_empty_transcript_handling():
    """4. Empty or whitespace transcript returns empty_input status without calling inference."""
    adapter = AIConversationAdapter()
    res = adapter.analyze_text("   ")
    assert res["status"] == "empty_input"
    assert "explanation" in res


def test_normal_conversation():
    """5. Normal harmless conversation analysis."""
    adapter = AIConversationAdapter()
    res = adapter.analyze_text("Hello, how are you today? Weather is nice.")
    assert res["status"] == "available"
    assert res["intent"]["type"] == "harmless_conversation"
    assert res["requested_action"]["type"] == "no_risky_action"


def test_financial_request_and_urgency():
    """6, 9. Financial transfer request with high urgency."""
    adapter = AIConversationAdapter()
    res = adapter.analyze_text("Send Rs 50,000 immediately to account 12345678.")
    assert res["status"] == "available"
    assert res["requested_action"]["type"] == "transfer_money"
    assert res["manipulation"]["urgency"] > 0.5


def test_otp_request():
    """7. OTP / credential theft request detection."""
    adapter = AIConversationAdapter()
    res = adapter.analyze_text("Please share your OTP immediately to verify your account.")
    assert res["status"] == "available"
    assert res["intent"]["type"] in ("credential_theft", "identity_verification", "information_request")


def test_remote_access_request():
    """8. Remote access installation request detection."""
    adapter = AIConversationAdapter()
    res = adapter.analyze_text("Download AnyDesk and grant remote access to your laptop.")
    assert res["status"] == "available"
    assert res["requested_action"]["type"] == "install_remote_access"


def test_secrecy_and_impersonation():
    """10, 11, 14, 15. Secrecy, family impersonation, confidence preservation."""
    adapter = AIConversationAdapter()
    fixture_text = "Hi Dad, I am in trouble. Don't tell anyone. Send 50,000 immediately."
    res = adapter.analyze_text(fixture_text)

    assert res["status"] == "available"
    assert res["impersonation"]["claimed_identity"] == "family_member"
    assert res["impersonation"]["possible_impersonation"] is True
    assert "confidence" in res["intent"]
    assert "confidence" in res["requested_action"]


def test_uninitialized_adapter_throws_unavailable():
    """Uninitialized adapter throws ConversationIntelligenceUnavailableError."""
    adapter = AIConversationAdapter()
    adapter._initialized = False
    adapter._readiness_status = "UNAVAILABLE"
    with patch.object(adapter, "initialize", return_value=False):
        with pytest.raises(ConversationIntelligenceUnavailableError):
            adapter.analyze_text("Test conversation")


def test_malformed_ai_output():
    """12. Exception during analyze_conversation raises ConversationIntelligenceFailedError."""
    adapter = AIConversationAdapter()
    adapter._analyze_fn = MagicMock(side_effect=ValueError("Corrupted result schema"))
    adapter._initialized = True
    adapter._readiness_status = "READY"

    with pytest.raises(ConversationIntelligenceFailedError):
        adapter.analyze_text("Hello test")


def test_inference_exception():
    """13. Exception during inference raises ConversationIntelligenceFailedError."""
    adapter = AIConversationAdapter()
    adapter._analyze_fn = MagicMock(side_effect=RuntimeError("AI model error"))
    adapter._initialized = True
    adapter._readiness_status = "READY"

    with pytest.raises(ConversationIntelligenceFailedError) as exc_info:
        adapter.analyze_text("Hello test")
    assert "AI model error" in str(exc_info.value)

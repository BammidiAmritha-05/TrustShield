import pytest
from unittest.mock import patch, MagicMock

from app.ai_adapter.protection import AIProtectionAdapter
from app.config import settings
from app.models import ProtectionAgentFailedError, ProtectionAgentUnavailableError


def test_adapter_import():
    """1. Protection adapter instantiation."""
    adapter = AIProtectionAdapter()
    assert adapter is not None


def test_ai_root_missing(monkeypatch):
    """2. AI root missing sets readiness to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "")
    adapter = AIProtectionAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"
    assert not adapter.is_available()


def test_ai_module_unavailable(monkeypatch):
    """3. Non-existent AI root directory sets readiness status to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "D:\\NonExistentPath\\ai")
    adapter = AIProtectionAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"


def test_low_risk_protection_guidance():
    """1. LOW_RISK yields SAFE protection level and NO_ACTION_REQUIRED."""
    adapter = AIProtectionAdapter()
    risk_assessment = {
        "status": "available",
        "risk_level": "SAFE",
        "risk_index": 10,
        "confidence": 0.95,
        "explanation": "Standard interaction."
    }

    res = adapter.generate_guidance(risk_assessment=risk_assessment)
    assert res["status"] == "available"
    assert res["protection_level"] == "SAFE"
    assert res["recommended_action"] == "NO_ACTION_REQUIRED"
    assert res["user_confirmation_required"] is False


def test_high_risk_financial_transfer_protection():
    """3, 7, 24, 25. HIGH_RISK money transfer yields PAUSE_TRANSFER and user_confirmation_required=True."""
    adapter = AIProtectionAdapter()
    risk_assessment = {
        "status": "available",
        "risk_level": "HIGH_RISK",
        "risk_index": 82,
        "confidence": 0.91,
        "explanation": "Financial transfer requested under urgency."
    }
    conv_analysis = {
        "requested_action": {"type": "transfer_money", "sensitivity": "critical", "confidence": 0.95},
        "manipulation": {"urgency": 0.95},
        "impersonation": {"claimed_identity": "family_member"}
    }

    res = adapter.generate_guidance(risk_assessment=risk_assessment, conversation_analysis=conv_analysis)
    assert res["status"] == "available"
    assert res["protection_level"] == "HIGH_RISK"
    assert res["recommended_action"] == "PAUSE_TRANSFER"
    assert res["user_confirmation_required"] is True
    assert "Pause the transfer" in res["do"]
    assert "Do NOT transfer" in res["do_not"]


def test_otp_request_protection():
    """6. OTP request yields DO_NOT_SHARE_OTP or PAUSE recommendation."""
    adapter = AIProtectionAdapter()
    risk_assessment = {
        "status": "available",
        "risk_level": "HIGH_RISK",
        "risk_index": 85,
        "confidence": 0.92,
        "explanation": "OTP requested."
    }
    conv_analysis = {
        "requested_action": {"type": "share_otp", "sensitivity": "critical", "confidence": 0.95},
        "manipulation": {"urgency": 0.90}
    }

    res = adapter.generate_guidance(risk_assessment=risk_assessment, conversation_analysis=conv_analysis)
    assert res["status"] == "available"
    assert res["user_confirmation_required"] is True
    assert "otp" in res["do_not"].lower() or "verification" in res["do_not"].lower() or "share" in res["do_not"].lower()


def test_aasist_semantic_invariant_in_protection():
    """23. Protection Agent MUST NOT describe synthetic_score as '95% scam probability'."""
    adapter = AIProtectionAdapter()
    risk_assessment = {
        "status": "available",
        "risk_level": "HIGH_RISK",
        "risk_index": 75,
        "confidence": 0.85,
        "explanation": "Voice appears synthetic."
    }

    res = adapter.generate_guidance(risk_assessment=risk_assessment)
    explanation_text = str(res.get("why", "")) + " " + str(res.get("do", ""))

    # Invariant: Must NOT claim scam probability
    assert "95% scam" not in explanation_text
    assert "95% fraud" not in explanation_text


def test_uninitialized_adapter_throws_unavailable():
    """Uninitialized adapter throws ProtectionAgentUnavailableError."""
    adapter = AIProtectionAdapter()
    adapter._initialized = False
    adapter._readiness_status = "UNAVAILABLE"
    with patch.object(adapter, "initialize", return_value=False):
        with pytest.raises(ProtectionAgentUnavailableError):
            adapter.generate_guidance({"risk_level": "HIGH_RISK"})


def test_guidance_generation_failure():
    """27. Exception during guidance generation raises ProtectionAgentFailedError."""
    adapter = AIProtectionAdapter()
    adapter._initialized = True
    adapter._agent_instance = MagicMock()
    adapter._agent_instance.generate_protection_guidance.side_effect = RuntimeError("Guidance failure")

    with pytest.raises(ProtectionAgentFailedError):
        adapter.generate_guidance({"risk_level": "HIGH_RISK"})

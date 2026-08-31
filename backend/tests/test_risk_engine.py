import pytest
from unittest.mock import patch, MagicMock

from app.ai_adapter.risk import AIRiskAdapter
from app.config import settings
from app.models import RiskEngineFailedError, RiskEngineUnavailableError
from app.services.evidence_store import SessionEvidenceStore


def test_adapter_import():
    """1. Risk adapter instantiation."""
    adapter = AIRiskAdapter()
    assert adapter is not None


def test_ai_root_missing(monkeypatch):
    """2. AI root missing sets readiness to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "")
    adapter = AIRiskAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"
    assert not adapter.is_available()


def test_ai_module_unavailable(monkeypatch):
    """3. Non-existent AI root directory sets readiness status to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "D:\\NonExistentPath\\ai")
    adapter = AIRiskAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"


def test_harmless_conversation_risk():
    """Empty / Harmless conversation yields LOW_RISK or UNCERTAIN risk."""
    adapter = AIRiskAdapter()
    store = SessionEvidenceStore()
    res = adapter.evaluate_session_turn("sess-1", conversation_analysis={"status": "available"}, evidence_store=store)

    assert res["status"] == "available"
    assert res["risk_level"] in ("LOW_RISK", "UNCERTAIN")


def test_financial_and_urgency_risk_escalation():
    """Financial request + high urgency escalates risk score."""
    adapter = AIRiskAdapter()
    store = SessionEvidenceStore()

    conv_payload = {
        "status": "available",
        "intent": {"type": "financial_fraud", "confidence": 0.90},
        "requested_action": {"type": "transfer_money", "sensitivity": "critical", "confidence": 0.95},
        "manipulation": {"urgency": 0.95, "secrecy": 0.0},
        "impersonation": {"claimed_identity": "family_member", "possible_impersonation": True, "confidence": 0.85},
        "explanation": "Request to transfer money with high urgency from family member."
    }

    res = adapter.evaluate_session_turn("sess-escalation", conversation_analysis=conv_payload, evidence_store=store)

    assert res["status"] == "available"
    assert res["risk_level"] in ("HIGH_RISK", "CRITICAL_RISK")
    assert res["risk_index"] >= 70
    assert "explanation" in res


def test_aasist_synthetic_score_invariant():
    """18. AASIST synthetic_score MUST remain a voice authenticity signal and NOT equal risk_score directly."""
    adapter = AIRiskAdapter()
    store = SessionEvidenceStore()

    voice_payload = {
        "status": "available",
        "synthetic_score": 0.95,
        "bona_fide_score": -6.5,
        "quality": "good"
    }

    # Evaluate voice analysis alone without risky conversation content
    res = adapter.evaluate_session_turn("sess-voice", voice_analysis=voice_payload, evidence_store=store)

    assert res["status"] == "available"
    # Mandatory Invariant: risk_score must NOT equal synthetic_score (0.95 * 100 = 95 != risk_index)
    # Synthetic voice alone contributes points but is NOT directly set equal to scam probability
    assert res["risk_index"] != 95
    assert res["risk_level"] != "CRITICAL_RISK"  # Voice alone without suspicious request is not critical risk


def test_uninitialized_adapter_throws_unavailable():
    """Uninitialized adapter throws RiskEngineUnavailableError."""
    adapter = AIRiskAdapter()
    adapter._initialized = False
    adapter._readiness_status = "UNAVAILABLE"
    with patch.object(adapter, "initialize", return_value=False):
        with pytest.raises(RiskEngineUnavailableError):
            adapter.evaluate_session_turn("sess-test")


def test_evaluation_failure():
    """19. Inference exception raises RiskEngineFailedError."""
    adapter = AIRiskAdapter()
    adapter._initialized = True
    adapter._risk_engine_cls = MagicMock()
    mock_store = MagicMock()
    mock_store.get_or_create_engine.side_effect = RuntimeError("Evaluation failure")

    with pytest.raises(RiskEngineFailedError):
        adapter.evaluate_session_turn("sess-err", evidence_store=mock_store)

import pytest
from unittest.mock import patch, MagicMock

from app.ai_adapter.claim import AIClaimVerificationAdapter
from app.config import settings
from app.models import ClaimVerificationFailedError, ClaimVerificationUnavailableError


def test_adapter_import():
    """1. Claim verification adapter instantiation."""
    adapter = AIClaimVerificationAdapter()
    assert adapter is not None


def test_ai_root_missing(monkeypatch):
    """2. AI root missing sets readiness to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "")
    adapter = AIClaimVerificationAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"
    assert not adapter.is_available()


def test_ai_module_unavailable(monkeypatch):
    """Non-existent AI root directory sets readiness status to UNAVAILABLE."""
    monkeypatch.setattr(settings, "TRUSTSHIELD_AI_ROOT", "D:\\NonExistentPath\\ai")
    adapter = AIClaimVerificationAdapter()
    assert adapter.get_readiness_status() == "UNAVAILABLE"


def test_empty_transcript_handling():
    """Empty or whitespace transcript returns empty_input status without calling inference."""
    adapter = AIClaimVerificationAdapter()
    res = adapter.verify_claim("   ")
    assert res["status"] == "empty_input"
    assert "explanation" in res


def test_pm_kisan_fee_contradicted_claim_verification():
    """3, 5, 6, 7, 8. PM-KISAN upfront processing fee claim yields CONTRADICTED status with Tier-1 provenance."""
    adapter = AIClaimVerificationAdapter()
    text = "I am calling regarding PM KISAN instalment. Processing fee required to receive instalment."
    res = adapter.verify_claim(text, simulate_live=False)

    assert res["status"] == "available"
    assert res["entity"]["name"] == "PM KISAN"
    assert res["verification"]["overall_status"] == "CONTRADICTED"
    assert 0.0 <= res["verification"]["confidence"] <= 1.0
    assert len(res["sources"]) > 0
    assert res["sources"][0]["url"] == "https://pmkisan.gov.in"
    assert res["sources"][0]["tier"] == "TIER_1"
    assert res["sources"][0]["evidence_origin"] in ("STATIC_REGISTRY", "LIVE_FETCH", "CACHE")


def test_harmless_text_no_claim_detected():
    """Harmless text returns NO_CLAIM_DETECTED status."""
    adapter = AIClaimVerificationAdapter()
    res = adapter.verify_claim("Hello how are you today?", simulate_live=False)

    assert res["status"] == "available"
    assert res["verification"]["overall_status"] == "NO_CLAIM_DETECTED"
    assert res["verification"]["confidence"] == 1.0


def test_retrieval_failure_yields_not_verified_not_scam():
    """9. Unrecognized / ambiguous entity yields NOT_VERIFIED (never SCAM or FALSE)."""
    adapter = AIClaimVerificationAdapter()
    text = "Claim regarding Unknown Unverified Fortune Lottery Scheme."
    res = adapter.verify_claim(text, simulate_live=False)

    assert res["status"] == "available"
    assert res["verification"]["overall_status"] == "NOT_VERIFIED"
    assert any("ambiguous" in lim.lower() or "does not prove" in lim.lower() for lim in res["limitations"])


def test_uninitialized_adapter_throws_unavailable():
    """Uninitialized adapter throws ClaimVerificationUnavailableError."""
    adapter = AIClaimVerificationAdapter()
    adapter._initialized = False
    adapter._readiness_status = "UNAVAILABLE"
    with patch.object(adapter, "initialize", return_value=False):
        with pytest.raises(ClaimVerificationUnavailableError):
            adapter.verify_claim("Test claim")


def test_verification_execution_failure():
    """10. Exception during claim verification raises ClaimVerificationFailedError."""
    adapter = AIClaimVerificationAdapter()
    adapter._initialized = True
    adapter._verify_fn = MagicMock(side_effect=RuntimeError("Verification error"))

    with pytest.raises(ClaimVerificationFailedError):
        adapter.verify_claim("Test claim")

from app.services.action_gate_service import ActionGateService


def make_risk(level):
    return {
        "status": "available",
        "risk_level": level,
        "risk_index": 80,
        "confidence": 0.90,
    }


def make_protection(level):
    return {
        "status": "available",
        "protection_level": level,
        "recommended_action": "PAUSE_TRANSFER",
        "user_confirmation_required": level not in ("SAFE", "UNCERTAIN"),
    }


def test_safe_action_is_allowed():
    service = ActionGateService()

    result = service.evaluate(
        make_risk("SAFE"),
        make_protection("SAFE"),
    )

    assert result["gate_decision"] == "ALLOW"
    assert result["can_proceed"] is True
    assert result["requires_verification"] is False


def test_caution_warns_user():
    service = ActionGateService()

    result = service.evaluate(
        make_risk("CAUTION"),
        make_protection("CAUTION"),
    )

    assert result["gate_decision"] == "WARN"
    assert result["can_proceed"] is True
    assert result["requires_verification"] is True


def test_suspicious_pauses_action():
    service = ActionGateService()

    result = service.evaluate(
        make_risk("SUSPICIOUS"),
        make_protection("SUSPICIOUS"),
    )

    assert result["gate_decision"] == "PAUSE_AND_VERIFY"
    assert result["can_proceed"] is False
    assert result["requires_verification"] is True


def test_high_risk_blocks_action():
    service = ActionGateService()

    result = service.evaluate(
        make_risk("HIGH_RISK"),
        make_protection("HIGH_RISK"),
    )

    assert result["gate_decision"] == "BLOCK_AND_VERIFY"
    assert result["can_proceed"] is False
    assert result["requires_verification"] is True


def test_uncertain_holds_action():
    service = ActionGateService()

    result = service.evaluate(
        make_risk("UNCERTAIN"),
        make_protection("UNCERTAIN"),
    )

    assert result["gate_decision"] == "HOLD_FOR_VERIFICATION"
    assert result["can_proceed"] is False
    assert result["requires_verification"] is True


def test_unknown_protection_level_defaults_to_uncertain():
    service = ActionGateService()

    result = service.evaluate(
        make_risk("UNKNOWN"),
        make_protection("UNKNOWN"),
    )

    assert result["gate_decision"] == "HOLD_FOR_VERIFICATION"
    assert result["can_proceed"] is False
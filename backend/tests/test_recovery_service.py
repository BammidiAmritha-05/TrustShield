from app.services.recovery_service import RecoveryService


def test_otp_sharing_requires_urgent_recovery():
    service = RecoveryService()

    result = service.generate_recovery_guidance(
        {"risk_level": "HIGH_RISK"},
        {"protection_level": "HIGH_RISK"},
        {"gate_decision": "BLOCK_AND_VERIFY"},
        {
            "requested_action": {
                "type": "share_otp"
            }
        },
    )

    assert result["recovery_required"] is True
    assert result["severity"] == "URGENT"
    assert result["action_type"] == "share_otp"
    assert result["external_action_taken"] is False
    assert result["loss_reversed"] is False
    assert len(result["steps"]) > 0


def test_money_transfer_preserves_evidence():
    service = RecoveryService()

    result = service.generate_recovery_guidance(
        {"risk_level": "HIGH_RISK"},
        {"protection_level": "HIGH_RISK"},
        {"gate_decision": "BLOCK_AND_VERIFY"},
        {
            "requested_action": {
                "type": "transfer_money"
            }
        },
    )

    assert result["recovery_required"] is True
    assert result["severity"] == "URGENT"
    assert result["evidence_preservation_recommended"] is True
    assert any(
        "transaction" in step.lower()
        for step in result["steps"]
    )


def test_safe_conversation_requires_no_recovery():
    service = RecoveryService()

    result = service.generate_recovery_guidance(
        {"risk_level": "SAFE"},
        {"protection_level": "SAFE"},
        {"gate_decision": "ALLOW"},
        {
            "requested_action": {
                "type": "no_risky_action"
            }
        },
    )

    assert result["recovery_required"] is False
    assert result["severity"] == "NONE"
    assert result["external_action_taken"] is False
    assert result["loss_reversed"] is False


def test_unknown_action_fails_safe():
    service = RecoveryService()

    result = service.generate_recovery_guidance(
        {"risk_level": "HIGH_RISK"},
        {"protection_level": "HIGH_RISK"},
        {"gate_decision": "BLOCK_AND_VERIFY"},
        {
            "requested_action": {
                "type": "some_future_unknown_action"
            }
        },
    )

    assert result["action_type"] == "some_future_unknown_action"
    assert result["recovery_required"] is False
    assert result["external_action_taken"] is False
    assert result["loss_reversed"] is False
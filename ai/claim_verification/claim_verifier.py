"""
Master Official Claim Verifier Module for TrustShield AI (Phase 5.6B).
Orchestrates multi-claim extraction, jurisdiction disambiguation, live source retrieval, and fail-safe comparison.
"""

from typing import Optional, Dict, Any
from ai.claim_verification.claim_schema import HardenedVerificationResult
from ai.claim_verification.claim_extractor import extract_claims_and_jurisdiction
from ai.claim_verification.source_retriever import retrieve_official_source_info
from ai.claim_verification.claim_comparator import compare_live_claims


def verify_official_claim(
    text: str,
    session_context: Optional[Dict[str, Any]] = None,
    simulate_live: bool = True,
    disable_static_summary: bool = False
) -> HardenedVerificationResult:
    """Extracts, retrieves live authoritative evidence, and verifies official claims with provenance & fail-safe rules.

    Args:
        text: Conversation text / transcript snippet.
        session_context: Optional session context dictionary.
        simulate_live: Whether to perform live HTTPS fetch.
        disable_static_summary: Test fixture flag to test live-only text extraction.

    Returns:
        Structured HardenedVerificationResult object.
    """
    # 1. Extract Entity, Claims Array, Action, and OTP Context
    entity_dict, claims_list, action_dict, otp_context = extract_claims_and_jurisdiction(text, session_context=session_context)

    if not entity_dict or not claims_list:
        return compare_live_claims(None, [], None, otp_context, None, None)

    # 2. Retrieve Live Authoritative Source Info
    source_info, live_res = retrieve_official_source_info(
        entity_dict.get("name", ""),
        entity_dict.get("jurisdiction", ""),
        simulate_live=simulate_live,
        disable_static_summary=disable_static_summary
    )

    # 3. Compare Claims against Live Authoritative Source Evidence
    result = compare_live_claims(entity_dict, claims_list, action_dict, otp_context, source_info, live_res)

    return result

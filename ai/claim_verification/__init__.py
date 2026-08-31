"""
TrustShield Official Claim Verification Package (Phase 5.6B).
"""

from ai.claim_verification.claim_schema import (
    ClaimStatus,
    ActionStatus,
    SourceTier,
    SourceType,
    FreshnessStatus,
    EvidenceOrigin,
    CurrentnessStatus,
    OTPContext,
    EntityInfo,
    ClaimItemInfo,
    ActionInfo,
    SourceInfo,
    VerificationSummary,
    HardenedVerificationResult,
)
from ai.claim_verification.source_validator import validate_official_url
from ai.claim_verification.freshness import determine_freshness, get_cached_response, set_cached_response
from ai.claim_verification.live_retriever import fetch_live_official_source
from ai.claim_verification.source_registry import AUTHORITATIVE_REGISTRY, lookup_authoritative_source_by_jurisdiction
from ai.claim_verification.claim_extractor import extract_claims_and_jurisdiction
from ai.claim_verification.source_retriever import retrieve_official_source_info
from ai.claim_verification.claim_comparator import compare_live_claims
from ai.claim_verification.claim_verifier import verify_official_claim

__all__ = [
    "ClaimStatus",
    "ActionStatus",
    "SourceTier",
    "SourceType",
    "FreshnessStatus",
    "EvidenceOrigin",
    "CurrentnessStatus",
    "OTPContext",
    "EntityInfo",
    "ClaimItemInfo",
    "ActionInfo",
    "SourceInfo",
    "VerificationSummary",
    "HardenedVerificationResult",
    "validate_official_url",
    "determine_freshness",
    "get_cached_response",
    "set_cached_response",
    "fetch_live_official_source",
    "AUTHORITATIVE_REGISTRY",
    "lookup_authoritative_source_by_jurisdiction",
    "extract_claims_and_jurisdiction",
    "retrieve_official_source_info",
    "compare_live_claims",
    "verify_official_claim"
]

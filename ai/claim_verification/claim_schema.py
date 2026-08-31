"""
Data Models and Audit Schemas for TrustShield Official Claim Verification Engine (Phase 5.6B).
Adds evidence provenance tracking (evidence_origin) and claim currentness (currentness).
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum


class ClaimStatus(str, Enum):
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    NO_CLAIM_DETECTED = "NO_CLAIM_DETECTED"


class ActionStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    NOT_VERIFIED = "NOT_VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    NONE = "NONE"


class SourceTier(str, Enum):
    TIER_1 = "TIER_1"  # Official government/institutional domain (.gov.in, official bank site)
    TIER_2 = "TIER_2"  # Official institutional publication / policy document
    TIER_3 = "TIER_3"  # Trusted secondary source
    UNTRUSTED = "UNTRUSTED"  # Blogs, forums, social media, unverified sites


class SourceType(str, Enum):
    STATIC_OFFICIAL_SOURCE = "STATIC_OFFICIAL_SOURCE"
    LIVE_OFFICIAL_SOURCE = "LIVE_OFFICIAL_SOURCE"


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    RECENT = "RECENT"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class EvidenceOrigin(str, Enum):
    LIVE_FETCH = "LIVE_FETCH"
    CACHE = "CACHE"
    STATIC_REGISTRY = "STATIC_REGISTRY"
    UNKNOWN = "UNKNOWN"


class CurrentnessStatus(str, Enum):
    CURRENT_SUPPORTED = "CURRENT_SUPPORTED"
    HISTORICAL = "HISTORICAL"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class OTPContext(str, Enum):
    USER_INITIATED_AUTHENTICATION = "user_initiated_official_authentication"
    INCOMING_REQUEST_TO_SHARE_OTP = "incoming_request_to_share_otp"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class EntityInfo:
    name: str
    type: str
    jurisdiction: str
    ambiguity: bool = False
    status: str = ClaimStatus.NOT_VERIFIED.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClaimItemInfo:
    text: str
    status: str = ClaimStatus.NOT_VERIFIED.value
    evidence: Optional[str] = None
    confidence: float = 0.0
    evidence_origin: str = EvidenceOrigin.UNKNOWN.value
    currentness: str = CurrentnessStatus.UNKNOWN.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "status": self.status,
            "evidence": self.evidence,
            "confidence": round(self.confidence, 2),
            "evidence_origin": self.evidence_origin,
            "currentness": self.currentness,
        }


@dataclass
class ActionInfo:
    type: str
    status: str = ActionStatus.NONE.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceInfo:
    url: str
    authority: str
    retrieved_at: str
    relevance: str
    tier: str = SourceTier.TIER_1.value
    source_type: str = SourceType.LIVE_OFFICIAL_SOURCE.value
    freshness: str = FreshnessStatus.FRESH.value
    evidence_origin: str = EvidenceOrigin.LIVE_FETCH.value
    http_status: int = 200
    content_length_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VerificationSummary:
    overall_status: str
    confidence: float
    otp_context: str = OTPContext.NOT_APPLICABLE.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "confidence": round(self.confidence, 2),
            "otp_context": self.otp_context,
        }


@dataclass
class HardenedVerificationResult:
    entity: EntityInfo
    claims: List[ClaimItemInfo] = field(default_factory=list)
    action: ActionInfo = field(default_factory=lambda: ActionInfo(type="none", status=ActionStatus.NONE.value))
    sources: List[SourceInfo] = field(default_factory=list)
    verification: VerificationSummary = field(default_factory=lambda: VerificationSummary(overall_status=ClaimStatus.NO_CLAIM_DETECTED.value, confidence=1.0))
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity": self.entity.to_dict(),
            "claims": [c.to_dict() for c in self.claims],
            "action": self.action.to_dict(),
            "sources": [s.to_dict() for s in self.sources],
            "verification": self.verification.to_dict(),
            "limitations": self.limitations,
        }

"""
Structured Verification Schemas and Data Models for TrustShield AI (Phase 4).
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum


class ProtectionLevel(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"
    UNCERTAIN = "UNCERTAIN"


@dataclass
class TrustedContact:
    id: str
    name: str
    relationship: str  # e.g., "brother", "father", "employer", "bank_branch"
    verification_channel: str  # e.g., "known phone number", "official portal", "direct office extension"
    verified_by_user: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GuidanceBlock:
    why: str
    do: str
    do_not: str
    verify: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VerificationPlan:
    protection_level: str
    recommended_action: str
    verification_method: str
    why: str
    do: str
    do_not: str
    verify: str
    draft_verification_message: Optional[str] = None
    confidence: float = 1.0
    trusted_contact_used: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protection_level": self.protection_level,
            "recommended_action": self.recommended_action,
            "verification_method": self.verification_method,
            "why": self.why,
            "do": self.do,
            "do_not": self.do_not,
            "verify": self.verify,
            "draft_verification_message": self.draft_verification_message,
            "confidence": round(self.confidence, 2),
            "trusted_contact_used": self.trusted_contact_used,
        }

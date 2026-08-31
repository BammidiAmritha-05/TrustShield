"""
Data schemas for TrustShield Conversation Intelligence Engine (Phase 2).
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class IntentCategory(str, Enum):
    FINANCIAL_FRAUD = "financial_fraud"
    CREDENTIAL_THEFT = "credential_theft"
    ACCOUNT_ACCESS = "account_access"
    IDENTITY_VERIFICATION = "identity_verification"
    REMOTE_ACCESS = "remote_access"
    PAYMENT_REQUEST = "payment_request"
    INFORMATION_REQUEST = "information_request"
    HARMLESS_CONVERSATION = "harmless_conversation"
    OTHER = "other"


class RequestedActionType(str, Enum):
    TRANSFER_MONEY = "transfer_money"
    SHARE_OTP = "share_otp"
    SHARE_PASSWORD = "share_password"
    SHARE_BANK_DETAILS = "share_bank_details"
    APPROVE_PAYMENT = "approve_payment"
    CLICK_LINK = "click_link"
    INSTALL_REMOTE_ACCESS = "install_remote_access"
    SHARE_IDENTITY_DOCUMENT = "share_identity_document"
    DISCLOSE_SENSITIVE_INFORMATION = "disclose_sensitive_information"
    CHANGE_ACCOUNT_DETAILS = "change_account_details"
    SHARE_VERIFICATION_CODE = "share_verification_code"
    NO_RISKY_ACTION = "no_risky_action"


class ActionSensitivity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ClaimedIdentityCategory(str, Enum):
    FAMILY_MEMBER = "family_member"
    BANK = "bank"
    POLICE = "police"
    GOVERNMENT = "government"
    EMPLOYER = "employer"
    EXECUTIVE = "executive"
    COLLEAGUE = "colleague"
    CUSTOMER_SUPPORT = "customer_support"
    DELIVERY_SERVICE = "delivery_service"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    type: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "confidence": round(self.confidence, 2)}


@dataclass
class ActionResult:
    type: str
    sensitivity: str
    confidence: float
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"type": self.type, "sensitivity": self.sensitivity, "confidence": round(self.confidence, 2)}
        if self.details:
            d["details"] = self.details
        return d


@dataclass
class ManipulationResult:
    urgency: float = 0.0
    secrecy: float = 0.0
    fear: float = 0.0
    authority_pressure: float = 0.0
    emotional_pressure: float = 0.0
    threat: float = 0.0
    reward: float = 0.0
    isolation: float = 0.0
    intimidation: float = 0.0
    forced_compliance: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "urgency": round(self.urgency, 2),
            "secrecy": round(self.secrecy, 2),
            "fear": round(self.fear, 2),
            "authority_pressure": round(self.authority_pressure, 2),
            "emotional_pressure": round(self.emotional_pressure, 2),
            "threat": round(self.threat, 2),
            "reward": round(self.reward, 2),
            "isolation": round(self.isolation, 2),
            "intimidation": round(self.intimidation, 2),
            "forced_compliance": round(self.forced_compliance, 2),
        }


@dataclass
class ImpersonationResult:
    claimed_identity: str
    possible_impersonation: bool
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claimed_identity": self.claimed_identity,
            "possible_impersonation": self.possible_impersonation,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class ContextResult:
    identity_verified: bool = False
    unusual_request: bool = False
    independent_verification_available: bool = False
    session_flags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "identity_verified": self.identity_verified,
            "unusual_request": self.unusual_request,
            "independent_verification_available": self.independent_verification_available,
        }
        if self.session_flags:
            d["session_flags"] = self.session_flags
        return d


@dataclass
class ConversationAnalysisResult:
    intent: IntentResult
    requested_action: ActionResult
    manipulation: ManipulationResult
    impersonation: ImpersonationResult
    context: ContextResult
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent.to_dict(),
            "requested_action": self.requested_action.to_dict(),
            "manipulation": self.manipulation.to_dict(),
            "impersonation": self.impersonation.to_dict(),
            "context": self.context.to_dict(),
            "explanation": self.explanation,
        }

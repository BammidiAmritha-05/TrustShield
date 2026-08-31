"""
Normalized Evidence Representation for TrustShield AI (Phase 3).
"""

import time
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class EvidenceSource(str, Enum):
    VOICE_MODEL = "VOICE_MODEL"
    TRANSCRIPT = "TRANSCRIPT"
    INTENT = "INTENT"
    ACTION = "ACTION"
    MANIPULATION = "MANIPULATION"
    IMPERSONATION = "IMPERSONATION"
    CONTEXT = "CONTEXT"
    RULE = "RULE"


# Default reliability ratings per evidence source (0.0 to 1.0)
SOURCE_RELIABILITY: Dict[str, float] = {
    EvidenceSource.VOICE_MODEL.value: 0.75,
    EvidenceSource.TRANSCRIPT.value: 0.90,
    EvidenceSource.INTENT.value: 0.85,
    EvidenceSource.ACTION.value: 0.95,
    EvidenceSource.MANIPULATION.value: 0.88,
    EvidenceSource.IMPERSONATION.value: 0.85,
    EvidenceSource.CONTEXT.value: 0.90,
    EvidenceSource.RULE.value: 0.95,
}


@dataclass
class NormalizedEvidence:
    signal: str
    value: Any
    confidence: float
    source: str
    timestamp: float = field(default_factory=time.time)
    reliability: float = 1.0
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    turn_index: int = 1

    def __post_init__(self):
        if self.source in SOURCE_RELIABILITY and self.reliability == 1.0:
            self.reliability = SOURCE_RELIABILITY[self.source]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "signal": self.signal,
            "value": self.value,
            "confidence": round(self.confidence, 2),
            "source": self.source,
            "timestamp": round(self.timestamp, 2),
            "reliability": round(self.reliability, 2),
            "turn_index": self.turn_index,
        }

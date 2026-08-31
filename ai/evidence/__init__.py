"""
TrustShield Evidence Subsystem Package (Phase 3).
"""

from ai.evidence.evidence_schema import NormalizedEvidence, EvidenceSource, SOURCE_RELIABILITY
from ai.evidence.evidence_accumulator import EvidenceAccumulator
from ai.evidence.temporal_engine import TemporalEngine

__all__ = [
    "NormalizedEvidence",
    "EvidenceSource",
    "SOURCE_RELIABILITY",
    "EvidenceAccumulator",
    "TemporalEngine"
]

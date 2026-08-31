"""
Confidence Calculation Module for TrustShield Risk Engine (Phase 3).
Calculates evidence confidence (0.0 to 1.0) separately from risk index.
"""

from typing import List, Dict, Any
from ai.evidence.evidence_schema import NormalizedEvidence, EvidenceSource


def calculate_confidence(evidence_items: List[NormalizedEvidence]) -> float:
    """Calculates an independent evidence confidence score from 0.0 to 1.0.

    Args:
        evidence_items: List of normalized evidence items.

    Returns:
        Confidence float between 0.0 and 1.0.
    """
    if not evidence_items:
        return 0.0

    total_weight = 0.0
    weighted_confidence_sum = 0.0

    has_transcript_evidence = False
    has_voice_evidence = False

    for item in evidence_items:
        # Weight evidence confidence by source reliability
        w = item.reliability
        weighted_confidence_sum += item.confidence * w
        total_weight += w

        if item.source in [EvidenceSource.TRANSCRIPT.value, EvidenceSource.ACTION.value, EvidenceSource.INTENT.value]:
            has_transcript_evidence = True
        if item.source == EvidenceSource.VOICE_MODEL.value:
            has_voice_evidence = True

    if total_weight == 0.0:
        return 0.0

    raw_conf = weighted_confidence_sum / total_weight

    # Confidence penalty if critical evidence channels are missing
    coverage_factor = 1.0
    if not has_transcript_evidence and not has_voice_evidence:
        coverage_factor = 0.20
    elif not has_transcript_evidence:
        coverage_factor = 0.60

    final_confidence = round(min(1.0, max(0.0, raw_conf * coverage_factor)), 2)
    return final_confidence

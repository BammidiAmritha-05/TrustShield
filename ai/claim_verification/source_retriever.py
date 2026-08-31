"""
Authoritative Live Source Retriever for TrustShield AI (Phase 5.6C).
Retrieves live official source data with 1-to-1 provenance alignment, HTTP status, and content length metadata.
"""

import time
from typing import Optional, Dict, Any, Tuple
from ai.claim_verification.claim_schema import SourceInfo, SourceTier, SourceType, FreshnessStatus, EvidenceOrigin
from ai.claim_verification.source_registry import lookup_authoritative_source_by_jurisdiction, RegistrySource
from ai.claim_verification.live_retriever import fetch_live_official_source


def retrieve_official_source_info(
    entity_name: str,
    jurisdiction: str,
    simulate_live: bool = True,
    disable_static_summary: bool = False
) -> Tuple[Optional[SourceInfo], Optional[Dict[str, Any]]]:
    """Retrieves live authoritative SourceInfo record matching entity and jurisdiction with strict provenance alignment.

    Args:
        entity_name: Name of extracted entity (e.g., YSR Rythu Bharosa, SBI, Customs).
        jurisdiction: State or government jurisdiction (e.g., Andhra Pradesh, Telangana, Central).
        simulate_live: Whether to perform live HTTPS fetch.
        disable_static_summary: Test fixture flag to test live-only text extraction.

    Returns:
        Tuple of (SourceInfo, live_fetch_dict).
    """
    if not entity_name or entity_name in ["Unknown", "Unverified Entity", "None"]:
        return None, None

    registry_entry: Optional[RegistrySource] = lookup_authoritative_source_by_jurisdiction(entity_name, jurisdiction)
    if not registry_entry:
        return None, None

    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Perform Safe Live HTTPS GET Request
    live_res = None
    if simulate_live:
        live_res = fetch_live_official_source(registry_entry.domain_url)

    if live_res:
        if live_res.get("status") == "success":
            freshness_val = live_res.get("freshness", FreshnessStatus.FRESH.value)
            retrieved_timestamp = live_res.get("retrieved_at", now_iso)
            origin_val = live_res.get("evidence_origin", EvidenceOrigin.LIVE_FETCH.value)
            http_code = live_res.get("http_status", 200)
            bytes_len = live_res.get("content_length_bytes", 0)
            snippet = live_res.get("text_snippet", "")

            relevance_text = f"Live fetched web snippet: {snippet[:200]}..." if (disable_static_summary or snippet) else f"Official policy summary: {registry_entry.official_policy_summary}"

            source_info = SourceInfo(
                url=registry_entry.domain_url,
                authority=f"{registry_entry.official_name} ({registry_entry.governing_body})",
                retrieved_at=retrieved_timestamp,
                relevance=relevance_text,
                tier=registry_entry.tier,
                source_type=SourceType.LIVE_OFFICIAL_SOURCE.value,
                freshness=freshness_val,
                evidence_origin=origin_val,
                http_status=http_code,
                content_length_bytes=bytes_len,
            )
            return source_info, live_res
        else:
            # Live Fetch Failed -> Fail-safe return with UNKNOWN origin and error status
            retrieved_timestamp = live_res.get("retrieved_at", now_iso)
            http_code = live_res.get("http_status", 504)
            source_info = SourceInfo(
                url=registry_entry.domain_url,
                authority=f"{registry_entry.official_name} ({registry_entry.governing_body})",
                retrieved_at=retrieved_timestamp,
                relevance=f"Live official source fetch failed ({live_res.get('reason')}).",
                tier=registry_entry.tier,
                source_type=SourceType.LIVE_OFFICIAL_SOURCE.value,
                freshness=FreshnessStatus.UNKNOWN.value,
                evidence_origin=EvidenceOrigin.UNKNOWN.value,
                http_status=http_code,
                content_length_bytes=0,
            )
            return source_info, live_res

    # Static Registry Fallback Mode (simulate_live = False explicitly)
    relevance_text = f"Official policy summary: {registry_entry.official_policy_summary}" if not disable_static_summary else "No live evidence snippet available."
    source_info = SourceInfo(
        url=registry_entry.domain_url,
        authority=f"{registry_entry.official_name} ({registry_entry.governing_body})",
        retrieved_at=now_iso,
        relevance=relevance_text,
        tier=registry_entry.tier,
        source_type=SourceType.STATIC_OFFICIAL_SOURCE.value,
        freshness=FreshnessStatus.FRESH.value,
        evidence_origin=EvidenceOrigin.STATIC_REGISTRY.value,
        http_status=200,
        content_length_bytes=0,
    )
    return source_info, live_res

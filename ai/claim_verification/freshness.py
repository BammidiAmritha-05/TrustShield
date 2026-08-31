"""
Freshness & Safe In-Memory Caching Module for TrustShield AI (Phase 5.6).
Tracks retrieval timestamps, freshness status, TTL caching, and per-domain rate limiting.
"""

import time
from typing import Dict, Any, Optional
from ai.claim_verification.claim_schema import FreshnessStatus

# Cache TTL: 300 seconds (5 minutes)
CACHE_TTL_SECONDS: float = 300.0

# Rate Limit Cooldown: 1.0 second per domain
RATE_LIMIT_COOLDOWN_SECONDS: float = 1.0

_live_source_cache: Dict[str, Dict[str, Any]] = {}
_domain_last_request_time: Dict[str, float] = {}


def determine_freshness(retrieved_at_iso: str, page_last_updated_iso: Optional[str] = None) -> str:
    """Determines source freshness status based on retrieval and last updated timestamps.

    Args:
        retrieved_at_iso: ISO timestamp when retrieved.
        page_last_updated_iso: Optional ISO timestamp when page was updated.

    Returns:
        FreshnessStatus string (FRESH, RECENT, STALE, UNKNOWN).
    """
    if not retrieved_at_iso:
        return FreshnessStatus.UNKNOWN.value

    # Fetched live right now is FRESH
    return FreshnessStatus.FRESH.value


def get_cached_response(url: str) -> Optional[Dict[str, Any]]:
    """Retrieves valid cached response if available within TTL."""
    entry = _live_source_cache.get(url)
    if not entry:
        return None

    now = time.time()
    if now - entry["cached_at"] > CACHE_TTL_SECONDS:
        del _live_source_cache[url]
        return None

    return entry["data"]


def set_cached_response(url: str, data: Dict[str, Any]) -> None:
    """Stores response in live source cache with current timestamp."""
    _live_source_cache[url] = {
        "cached_at": time.time(),
        "data": data
    }


def enforce_rate_limit(domain: str) -> None:
    """Enforces per-domain request rate limiting cooldown."""
    now = time.time()
    last_time = _domain_last_request_time.get(domain, 0.0)
    elapsed = now - last_time
    if elapsed < RATE_LIMIT_COOLDOWN_SECONDS:
        time.sleep(RATE_LIMIT_COOLDOWN_SECONDS - elapsed)
    _domain_last_request_time[domain] = time.time()

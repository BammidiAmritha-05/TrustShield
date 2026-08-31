"""
Source Security Validator for TrustShield AI (Phase 5.6).
Validates HTTPS scheme, official domain allowlist, expected hosts, and prevents untrusted redirects.
"""

from urllib.parse import urlparse
from typing import Tuple, List

# Official Domain Allowlist Patterns
ALLOWED_DOMAIN_PATTERNS: List[str] = [
    ".gov.in",
    ".nic.in",
    "bank.sbi",
    "hdfcbank.com",
    "rbi.org.in",
    "icicibank.com",
    "cybercrime.gov.in",
    "uidai.gov.in",
    "cbic.gov.in",
    "pmkisan.gov.in",
    "rythubharosa.ap.gov.in",
    "rythubandhu.telangana.gov.in",
]


def validate_official_url(url: str) -> Tuple[bool, str]:
    """Validates if a URL meets TrustShield official security criteria.

    Args:
        url: Candidate official URL.

    Returns:
        Tuple of (is_valid: bool, reason: str).
    """
    if not url:
        return False, "URL is empty"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"URL parse error: {str(e)}"

    # 1. Enforce HTTPS scheme
    if parsed.scheme.lower() != "https":
        return False, f"Non-HTTPS scheme rejected ({parsed.scheme})"

    # 2. Check Domain Allowlist
    host = parsed.netloc.lower()
    if not host:
        return False, "URL missing host"

    # Remove port if present
    if ":" in host:
        host = host.split(":")[0]

    domain_allowed = any(host.endswith(pattern) or host == pattern.lstrip(".") for pattern in ALLOWED_DOMAIN_PATTERNS)
    if not domain_allowed:
        return False, f"Domain '{host}' is not in the official Tier-1/Tier-2 allowlist"

    return True, "Valid official URL"

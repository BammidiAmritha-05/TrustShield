"""
Safe Live Official Source Retriever for TrustShield AI (Phase 5.6C).
Performs read-only, rate-limited, cached HTTPS GET requests to allowlisted official domains
with strict Anti-Prompt-Injection safeguards, content length metadata, and provenance tracking.
"""

import time
import re
import urllib.request
from urllib.parse import urlparse
from html.parser import HTMLParser
from typing import Dict, Any, Optional
from ai.claim_verification.claim_schema import EvidenceOrigin, SourceType
from ai.claim_verification.source_validator import validate_official_url
from ai.claim_verification.freshness import (
    get_cached_response,
    set_cached_response,
    enforce_rate_limit,
    determine_freshness,
)


class TextExtractHTMLParser(HTMLParser):
    """Simple safe HTML parser stripping tags and collecting clean text."""

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_tags = {"script", "style", "head", "meta", "noscript"}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()

    def handle_endtag(self, tag):
        self.current_tag = None

    def handle_data(self, data):
        if self.current_tag not in self.skip_tags:
            cleaned = data.strip()
            if cleaned:
                self.text_parts.append(cleaned)

    def get_text(self) -> str:
        return " ".join(self.text_parts)


def sanitize_webpage_text_anti_prompt_injection(text: str) -> str:
    """Neutralizes potential prompt-injection instructions embedded in retrieved webpage content.

    Args:
        text: Raw extracted webpage text.

    Returns:
        Sanitized text safe for evidence extraction.
    """
    if not text:
        return ""

    injection_patterns = [
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"disregard\s+(?:all\s+)?prior\s+instructions",
        r"you\s+are\s+now\s+a",
        r"system\s+prompt",
        r"override\s+safety\s+rules",
        r"act\s+as\s+an?\s+unrestricted",
    ]

    sanitized = text
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, "[UNTRUSTED_INSTRUCTION_STRIPPED]", sanitized, flags=re.IGNORECASE)

    return sanitized


def fetch_live_official_source(url: str, expected_host: Optional[str] = None) -> Dict[str, Any]:
    """Safely retrieves live official source content from an allowlisted URL.

    Args:
        url: Allowlisted HTTPS URL.
        expected_host: Optional expected host for validation.

    Returns:
        Dict containing status, text_snippet, retrieved_at, freshness, evidence_origin, source_type, and HTTP metadata.
    """
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # 1. Security Validation
    valid, reason = validate_official_url(url)
    if not valid:
        return {
            "status": "blocked",
            "reason": f"Security validation failed: {reason}",
            "retrieved_at": now_iso,
            "url": url,
            "http_status": 403,
            "content_length_bytes": 0,
            "evidence_origin": EvidenceOrigin.UNKNOWN.value,
            "source_type": SourceType.LIVE_OFFICIAL_SOURCE.value,
        }

    # 2. Check Cache
    cached = get_cached_response(url)
    if cached:
        cached_copy = dict(cached)
        cached_copy["evidence_origin"] = EvidenceOrigin.CACHE.value
        cached_copy["source_type"] = SourceType.LIVE_OFFICIAL_SOURCE.value
        return cached_copy

    # 3. Rate Limit Enforce
    domain = urlparse(url).netloc
    enforce_rate_limit(domain)

    # 4. Perform Safe Read-Only HTTPS GET Request
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TrustShieldAI-VerificationCopilot/1.0 (+https://trustshield.ai)"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=3.0) as response:
            http_code = response.status
            if http_code != 200:
                return {
                    "status": "failed",
                    "reason": f"HTTP status {http_code}",
                    "retrieved_at": now_iso,
                    "url": url,
                    "http_status": http_code,
                    "content_length_bytes": 0,
                    "evidence_origin": EvidenceOrigin.UNKNOWN.value,
                    "source_type": SourceType.LIVE_OFFICIAL_SOURCE.value,
                }

            # Enforce max payload size limit (500 KB)
            raw_bytes = response.read(512000)
            content_len = len(raw_bytes)
            content_type = response.headers.get("Content-Type", "")

            # Extract Clean Text
            html_str = raw_bytes.decode("utf-8", errors="ignore")
            parser = TextExtractHTMLParser()
            parser.feed(html_str)
            raw_text = parser.get_text()

            # Apply Anti-Prompt-Injection Safeguard
            clean_text = sanitize_webpage_text_anti_prompt_injection(raw_text)

            res_data = {
                "status": "success",
                "retrieved_at": now_iso,
                "url": url,
                "domain": domain,
                "http_status": http_code,
                "content_length_bytes": content_len,
                "content_type": content_type,
                "text_snippet": clean_text[:2000],  # Concise snippet
                "freshness": determine_freshness(now_iso),
                "evidence_origin": EvidenceOrigin.LIVE_FETCH.value,
                "source_type": SourceType.LIVE_OFFICIAL_SOURCE.value,
            }

            set_cached_response(url, res_data)
            return res_data

    except Exception as e:
        return {
            "status": "failed",
            "reason": f"Live fetch error: {str(e)}",
            "retrieved_at": now_iso,
            "url": url,
            "http_status": 504,
            "content_length_bytes": 0,
            "evidence_origin": EvidenceOrigin.UNKNOWN.value,
            "source_type": SourceType.LIVE_OFFICIAL_SOURCE.value,
        }

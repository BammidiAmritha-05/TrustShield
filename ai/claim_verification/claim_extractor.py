"""
Claim & Jurisdiction Extraction Module for TrustShield AI (Phase 5.6B).
Supports multi-claim extraction, jurisdiction disambiguation, claim importance gating, and OTP context parsing.
"""

import re
from typing import Optional, Dict, Any, List, Tuple
from ai.claim_verification.claim_schema import OTPContext


def extract_claims_and_jurisdiction(text: str, session_context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]], Optional[Dict[str, Any]], str]:
    """Extracts entity, claims array, action, and OTP context from conversation text.

    Args:
        text: Conversation text / transcript snippet.
        session_context: Optional session context dictionary.

    Returns:
        Tuple of (entity_dict, list_of_claim_dicts, action_dict, otp_context_string).
    """
    text_lower = text.lower()

    # Claim Importance Gate: Filter harmless conversational text
    safety_relevant_keywords = [
        "rythu", "pm kisan", "pm-kisan", "sbi", "hdfc", "bank", "customs", "courier", "fedex",
        "police", "cbi", "cyber crime", "digital arrest", "warrant", "aadhaar", "uidai",
        "wire transfer", "ceo", "employer", "otp", "password", "subsidy", "scheme", "grant", "lottery",
        "services", "renewal", "untrusted", "phishing"
    ]
    if not any(k in text_lower for k in safety_relevant_keywords):
        return None, [], None, OTPContext.NOT_APPLICABLE.value

    # 1. Determine OTP Context precisely
    otp_context = OTPContext.NOT_APPLICABLE.value
    if "otp" in text_lower or "password" in text_lower or "verification code" in text_lower:
        if any(k in text_lower for k in [
            "tell me", "send otp", "read out", "share otp", "provide otp", "give me the otp",
            "otp cheppu", "otp batao", "otp bol", "otp kudu", "otp sollu"
        ]):
            otp_context = OTPContext.INCOMING_REQUEST_TO_SHARE_OTP.value
        elif any(k in text_lower for k in ["log in", "login", "enter otp on", "official website", "user initiated", "your own device"]):
            otp_context = OTPContext.USER_INITIATED_AUTHENTICATION.value
        else:
            otp_context = OTPContext.UNKNOWN.value

    claims_list: List[Dict[str, Any]] = []

    # 2. Scheme / Entity & Jurisdiction Disambiguation
    if "rythu bharosa" in text_lower or "rythu bandhu" in text_lower:
        if "ysr" in text_lower or "andhra" in text_lower or "ap" in text_lower:
            entity_name = "YSR Rythu Bharosa"
            jurisdiction = "Andhra Pradesh"
            ambiguity = False
        elif "telangana" in text_lower or "tg" in text_lower or "rythu bandhu" in text_lower:
            entity_name = "Telangana Rythu Bharosa"
            jurisdiction = "Telangana"
            ambiguity = False
        else:
            entity_name = "Rythu Bharosa"
            jurisdiction = "Unknown"
            ambiguity = True

        claims_list.append({"text": text})

        # Support Multi-Claim (e.g. Claim 2: Fee requirement). Word boundary check so "payment" does not match "pay"
        if re.search(r"\b(?:pay fee|processing fee|upfront fee|transfer fee|fee to claim|charge|pay ₹|pay rs)\b", text_lower):
            claims_list.append({"text": "Processing fee or upfront money transfer is required to receive funds."})

        action_type = "share_otp" if otp_context == OTPContext.INCOMING_REQUEST_TO_SHARE_OTP.value else ("transfer_money" if re.search(r"\b(?:send money|pay fee|transfer money|pay penalty|pay ₹|pay rs)\b", text_lower) else "none")

        return (
            {"name": entity_name, "type": "government_scheme", "jurisdiction": jurisdiction, "ambiguity": ambiguity},
            claims_list,
            {"type": action_type},
            otp_context
        )

    if "pm kisan" in text_lower or "pm-kisan" in text_lower:
        claims_list.append({"text": text})
        if re.search(r"\b(?:pay fee|verification fee|processing fee|charge|pay ₹|pay rs)\b", text_lower):
            claims_list.append({"text": "Verification fee required to receive PM-KISAN instalment."})

        action_type = "share_otp" if otp_context == OTPContext.INCOMING_REQUEST_TO_SHARE_OTP.value else ("transfer_money" if re.search(r"\b(?:send money|pay fee|transfer money|pay ₹|pay rs)\b", text_lower) else "none")
        return (
            {"name": "PM KISAN", "type": "government_scheme", "jurisdiction": "Central", "ambiguity": False},
            claims_list,
            {"type": action_type},
            otp_context
        )

    # 3. UIDAI / Aadhaar Portal Claims
    if "uidai" in text_lower or ("aadhaar" in text_lower and not any(k in text_lower for k in ["police", "warrant", "arrest", "cbi"])):
        claims_list.append({"text": text})
        return (
            {"name": "Aadhaar", "type": "government_notice", "jurisdiction": "Central", "ambiguity": False},
            claims_list,
            {"type": "none"},
            otp_context
        )

    # 4. Bank Security Claims
    if any(k in text_lower for k in ["sbi", "hdfc", "bank manager", "customer care", "card is blocked", "account suspended", "netbanking"]):
        entity_name = "SBI" if "sbi" in text_lower else ("HDFC Bank" if "hdfc" in text_lower else "Bank")
        claims_list.append({"text": text})

        # Check for untrusted / phishing URL in text
        if "http://" in text_lower or "untrusted" in text_lower or "phishing" in text_lower:
            action_type = "click_link"
        else:
            action_type = "share_otp" if otp_context == OTPContext.INCOMING_REQUEST_TO_SHARE_OTP.value else ("share_password" if "password" in text_lower else "none")

        return (
            {"name": entity_name, "type": "bank", "jurisdiction": "Central", "ambiguity": False},
            claims_list,
            {"type": action_type},
            otp_context
        )

    # 5. Employer Directives
    if any(k in text_lower for k in ["ceo", "employer", "boss", "manager", "confidential acquisition", "wire transfer"]):
        claims_list.append({"text": text})
        action_type = "transfer_money" if any(k in text_lower for k in ["transfer", "send", "pay", "wire"]) else "none"
        return (
            {"name": "Employer", "type": "employer_instruction", "jurisdiction": "Corporate", "ambiguity": False},
            claims_list,
            {"type": action_type},
            otp_context
        )

    # 6. Law Enforcement Notices
    if any(k in text_lower for k in ["police", "cbi", "cyber crime", "digital arrest", "warrant"]):
        claims_list.append({"text": text})
        action_type = "transfer_money" if any(k in text_lower for k in ["transfer", "send", "pay"]) else ("share_identity_document" if "aadhaar" in text_lower else "none")
        return (
            {"name": "Cyber Crime Police", "type": "law_enforcement_notice", "jurisdiction": "Central", "ambiguity": False},
            claims_list,
            {"type": action_type},
            otp_context
        )

    # 7. Courier / Customs Claims
    if any(k in text_lower for k in ["fedex", "courier", "customs", "illegal package", "seized"]):
        claims_list.append({"text": text})
        action_type = "transfer_money" if any(k in text_lower for k in ["pay", "penalty", "transfer", "fee"]) else "none"
        return (
            {"name": "Customs", "type": "delivery_customs_claim", "jurisdiction": "Central", "ambiguity": False},
            claims_list,
            {"type": action_type},
            otp_context
        )

    # 8. Unregistered / General Scheme / Services Claims
    if any(k in text_lower for k in ["scheme", "subsidy", "lottery", "fortune", "grant", "services", "renewal"]):
        match = re.search(r"([a-z0-9\s]+(?:scheme|subsidy|services|fortune|lottery))", text_lower)
        entity_name = match.group(1).title().strip() if match else "Unverified Entity"
        claims_list.append({"text": text})
        action_type = "share_otp" if otp_context == OTPContext.INCOMING_REQUEST_TO_SHARE_OTP.value else ("transfer_money" if any(k in text_lower for k in ["send", "pay", "transfer"]) else "none")
        return (
            {"name": entity_name, "type": "government_scheme", "jurisdiction": "Unknown", "ambiguity": True},
            claims_list,
            {"type": action_type},
            otp_context
        )

    return None, [], None, otp_context

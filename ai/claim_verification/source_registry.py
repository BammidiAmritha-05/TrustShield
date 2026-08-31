"""
Authoritative Live Source Registry for TrustShield AI (Phase 5.6).
Contains verified official policies, live endpoints, source tiers, and jurisdiction rules.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from ai.claim_verification.claim_schema import SourceTier, SourceType


@dataclass
class RegistrySource:
    source_id: str
    entity: str
    official_name: str
    jurisdiction: str  # e.g., "Andhra Pradesh", "Telangana", "Central"
    domain_url: str
    governing_body: str
    official_policy_summary: str
    allows_phone_otp_requests: bool = False
    allows_phone_money_transfers: bool = False
    tier: str = SourceTier.TIER_1.value
    source_type: str = SourceType.LIVE_OFFICIAL_SOURCE.value


AUTHORITATIVE_REGISTRY: List[RegistrySource] = [
    # 1. YSR Rythu Bharosa (Andhra Pradesh)
    RegistrySource(
        source_id="AP_YSR_RYTHU_BHAROSA",
        entity="YSR Rythu Bharosa",
        official_name="YSR Rythu Bharosa Portal",
        jurisdiction="Andhra Pradesh",
        domain_url="https://rythubharosa.ap.gov.in",
        governing_body="Department of Agriculture, Government of Andhra Pradesh",
        official_policy_summary="Financial assistance is directly credited to beneficiary bank accounts via Direct Benefit Transfer (DBT). No OTP, fee, or payment transfer is ever requested over incoming phone calls.",
        allows_phone_otp_requests=False,
        allows_phone_money_transfers=False
    ),

    # 2. Telangana Rythu Bharosa / Rythu Bandhu (Telangana)
    RegistrySource(
        source_id="TELANGANA_RYTHU_BHAROSA",
        entity="Telangana Rythu Bharosa",
        official_name="Telangana Rythu Bandhu Portal",
        jurisdiction="Telangana",
        domain_url="https://rythubandhu.telangana.gov.in",
        governing_body="Department of Agriculture, Government of Telangana",
        official_policy_summary="Agricultural investment support is directly deposited into registered farmers' accounts via treasury DBT. Officials do not request OTP disclosure or phone fees.",
        allows_phone_otp_requests=False,
        allows_phone_money_transfers=False
    ),

    # 3. PM-KISAN Samman Nidhi (Central / India)
    RegistrySource(
        source_id="PM_KISAN",
        entity="PM KISAN",
        official_name="Pradhan Mantri Kisan Samman Nidhi Portal",
        jurisdiction="Central",
        domain_url="https://pmkisan.gov.in",
        governing_body="Ministry of Agriculture & Farmers Welfare, Government of India",
        official_policy_summary="Instalment payouts are directly remitted via Aadhaar-seeded bank accounts. Officials do not request OTPs, PINs, or fee transfers to process payouts. OTP authentication is used on portal for e-KYC.",
        allows_phone_otp_requests=False,
        allows_phone_money_transfers=False
    ),

    # 4. SBI (State Bank of India)
    RegistrySource(
        source_id="BANK_SBI",
        entity="SBI",
        official_name="State Bank of India Official Security Portal",
        jurisdiction="Central",
        domain_url="https://bank.sbi",
        governing_body="Reserve Bank of India (RBI) Regulated Financial Institution",
        official_policy_summary="SBI representatives will NEVER ask for confidential details like OTP, UPI PIN, CVV, or NetBanking password over incoming phone calls, SMS, or email.",
        allows_phone_otp_requests=False,
        allows_phone_money_transfers=False
    ),

    # 5. HDFC Bank
    RegistrySource(
        source_id="BANK_HDFC",
        entity="HDFC Bank",
        official_name="HDFC Bank Cyber Security Portal",
        jurisdiction="Central",
        domain_url="https://www.hdfcbank.com",
        governing_body="Reserve Bank of India (RBI) Regulated Financial Institution",
        official_policy_summary="HDFC Bank never calls customers demanding OTPs, passwords, or remote access app downloads to unblock cards or verify accounts.",
        allows_phone_otp_requests=False,
        allows_phone_money_transfers=False
    ),

    # 6. Reserve Bank of India (RBI)
    RegistrySource(
        source_id="GOV_RBI",
        entity="Reserve Bank of India",
        official_name="RBI Kehta Hai Financial Awareness Portal",
        jurisdiction="Central",
        domain_url="https://rbikehtahai.rbi.org.in",
        governing_body="Reserve Bank of India",
        official_policy_summary="RBI does not maintain individual bank accounts, hold funds for public release, or demand fees/taxes to unfreeze bank accounts.",
        allows_phone_otp_requests=False,
        allows_phone_money_transfers=False
    ),

    # 7. Indian Customs (CBIC)
    RegistrySource(
        source_id="GOV_CUSTOMS",
        entity="Customs",
        official_name="Central Board of Indirect Taxes and Customs (CBIC)",
        jurisdiction="Central",
        domain_url="https://www.cbic.gov.in",
        governing_body="Ministry of Finance, Government of India",
        official_policy_summary="Indian Customs officers do not call individuals via phone or messaging apps demanding immediate UPI payments or penalties for parcel release.",
        allows_phone_otp_requests=False,
        allows_phone_money_transfers=False
    ),

    # 8. UIDAI / Aadhaar
    RegistrySource(
        source_id="GOV_UIDAI",
        entity="Aadhaar",
        official_name="Unique Identification Authority of India (UIDAI)",
        jurisdiction="Central",
        domain_url="https://uidai.gov.in",
        governing_body="Ministry of Electronics and Information Technology, Government of India",
        official_policy_summary="UIDAI does not issue digital arrests, nor does it demand money transfer to verify Aadhaar identity.",
        allows_phone_otp_requests=False,
        allows_phone_money_transfers=False
    ),

    # 9. CERT-In / I4C Cyber Crime Portal
    RegistrySource(
        source_id="GOV_CERT_IN",
        entity="Cyber Crime",
        official_name="Indian Cyber Crime Coordination Centre (I4C) & CERT-In",
        jurisdiction="Central",
        domain_url="https://cybercrime.gov.in",
        governing_body="Ministry of Home Affairs, Government of India",
        official_policy_summary="Law enforcement agencies do not conduct 'digital arrests' over video calls or demand funds transfer to 'police clearance accounts'.",
        allows_phone_otp_requests=False,
        allows_phone_money_transfers=False
    ),
]


def lookup_authoritative_source_by_jurisdiction(entity_query: str, jurisdiction_query: str) -> Optional[RegistrySource]:
    """Look up an authoritative source in the registry matching entity name and jurisdiction.

    Args:
        entity_query: Extracted entity or scheme string.
        jurisdiction_query: Target jurisdiction state or region.

    Returns:
        Matching RegistrySource or None if no official source registered for that jurisdiction.
    """
    eq_lower = entity_query.lower()
    jq_lower = jurisdiction_query.lower()

    for source in AUTHORITATIVE_REGISTRY:
        if (
            source.entity.lower() in eq_lower or eq_lower in source.entity.lower()
        ):
            if jq_lower == "unknown" or jq_lower in source.jurisdiction.lower() or source.jurisdiction.lower() in jq_lower:
                return source

    return None

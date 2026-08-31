"""
Untouched Holdout Evaluation Dataset (15 scenarios) for TrustShield Risk Engine (Phase 3).
Used strictly for final validation after development tuning.
"""

from typing import List, Dict, Any

HOLDOUT_SCENARIOS: List[Dict[str, Any]] = [
    # 1. Paraphrased High Risk Scam: Emergency Money Demand
    {
        "id": "HOLDOUT_01",
        "category": "C. High-risk scams (Paraphrase)",
        "text": "Grandma, I am stuck at police station in London! Need 1000 dollars right away for bail, please keep it between us!",
        "session_context": {"claimed_role": "family_member", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # 2. Paraphrased High Risk Scam: Bank Credential Theft
    {
        "id": "HOLDOUT_02",
        "category": "C. High-risk scams (Paraphrase)",
        "text": "This is bank security desk. Your netbanking access is suspended. Provide your password immediately to reactivate.",
        "session_context": {"claimed_role": "bank", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # 3. Paraphrased Remote Access Scam
    {
        "id": "HOLDOUT_03",
        "category": "J. Remote-access scenarios (Paraphrase)",
        "text": "Microsoft support calling: Critical malware active on laptop. Install QuickSupport app now to share screen.",
        "session_context": {"claimed_role": "customer_support", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # 4. Paraphrased Digital Arrest Extortion
    {
        "id": "HOLDOUT_04",
        "category": "K. Digital-arrest style scenarios (Paraphrase)",
        "text": "CBI Officer speaking: Money laundering case filed against your name. Remain on line and transfer ₹1,00,000 to clearance account.",
        "session_context": {"claimed_role": "police", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # 5. Benign Family Interaction with Small Transfer
    {
        "id": "HOLDOUT_05",
        "category": "D. Benign financial requests",
        "text": "Can you GPay me ₹150 for cab fare?",
        "session_context": {"claimed_role": "family_member", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # 6. Benign Urgent Work Request
    {
        "id": "HOLDOUT_06",
        "category": "E. Benign urgent conversations",
        "text": "Please join the Zoom meeting right now, the client is waiting!",
        "session_context": {"claimed_role": "colleague", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # 7. Benign Bank Notice without Risky Action
    {
        "id": "HOLDOUT_07",
        "category": "H. Bank conversations",
        "text": "Dear customer, your quarterly bank statement is now available in your online portal.",
        "session_context": {"claimed_role": "bank", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # 8. Benign OTP Security Advisory
    {
        "id": "HOLDOUT_08",
        "category": "F. Benign OTP discussions",
        "text": "Security Alert: Never share your OTP with anyone claiming to be a bank agent.",
        "session_context": {"claimed_role": "system", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # 9. Courier Scam Paraphrase
    {
        "id": "HOLDOUT_09",
        "category": "L. Delivery/courier scenarios (Paraphrase)",
        "text": "Customs department: Package contains illegal narcotics. Pay clearance fee of ₹25,000 within 1 hour.",
        "session_context": {"claimed_role": "government", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # 10. CEO Fraud Paraphrase
    {
        "id": "HOLDOUT_10",
        "category": "I. Employer/CEO conversations (Paraphrase)",
        "text": "I am in urgent client meeting. Process ₹3,00,000 payment immediately, keep confidential.",
        "session_context": {"claimed_role": "executive", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # 11. Sarcastic / Quoted Text (Adversarial)
    {
        "id": "HOLDOUT_11",
        "category": "Adversarial / Quoted text",
        "text": "My friend got a fake call saying 'Send money immediately'. Can you believe people fall for that?",
        "session_context": {"claimed_role": "friend", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # 12. Noisy Audio Unusable Rejection
    {
        "id": "HOLDOUT_12",
        "category": "Uncertain / Unusable Audio",
        "text": "",
        "voice_analysis": {"status": "insufficient_evidence", "reason": "unusable_audio"},
        "session_context": {"claimed_role": "unknown", "identity_verified": False},
        "expected_risk_level": "UNCERTAIN",
    },

    # 13. Short Audio Rejection
    {
        "id": "HOLDOUT_13",
        "category": "Uncertain / Short Audio",
        "text": "",
        "voice_analysis": {"status": "insufficient_evidence", "reason": "audio_too_short"},
        "session_context": {"claimed_role": "unknown", "identity_verified": False},
        "expected_risk_level": "UNCERTAIN",
    },

    # 14. Suspicious Identity Verification Request
    {
        "id": "HOLDOUT_14",
        "category": "B. Suspicious conversations",
        "text": "Send a clear photo of your Aadhaar card and PAN card right now for urgent profile verification.",
        "session_context": {"claimed_role": "customer_support", "identity_verified": False},
        "expected_risk_level": "SUSPICIOUS",
    },

    # 15. Harmless Casual Chat
    {
        "id": "HOLDOUT_15",
        "category": "A. Normal conversations",
        "text": "Good morning! Hope you have a wonderful weekend ahead.",
        "session_context": {"claimed_role": "colleague", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
]

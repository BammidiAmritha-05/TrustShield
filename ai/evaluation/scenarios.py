"""
Development Evaluation Scenarios (35 cases) for TrustShield Risk Engine (Phase 3).
Covers categories A through L with paraphrases and edge cases.
"""

from typing import List, Dict, Any

DEV_SCENARIOS: List[Dict[str, Any]] = [
    # A. Normal Conversations
    {
        "id": "DEV_01",
        "category": "A. Normal conversations",
        "text": "Hi Mom, how are you? Are we still meeting for dinner tonight at 8 PM?",
        "session_context": {"claimed_role": "family_member", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
    {
        "id": "DEV_02",
        "category": "A. Normal conversations",
        "text": "Hey Rahul, let's connect tomorrow morning to discuss the project slides.",
        "session_context": {"claimed_role": "colleague", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
    {
        "id": "DEV_03",
        "category": "A. Normal conversations",
        "text": "Good afternoon, I am calling to follow up on your recent customer service inquiry regarding product delivery.",
        "session_context": {"claimed_role": "customer_support", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # B. Suspicious Conversations
    {
        "id": "DEV_04",
        "category": "B. Suspicious conversations",
        "text": "This is an urgent security notification from bank support. Unverified activity detected. Keep this confidential.",
        "session_context": {"claimed_role": "bank", "identity_verified": False},
        "expected_risk_level": "SUSPICIOUS",
    },
    {
        "id": "DEV_05",
        "category": "B. Suspicious conversations",
        "text": "I am calling from your service provider. Your account requires immediate verification or it will be suspended today.",
        "session_context": {"claimed_role": "customer_support", "identity_verified": False},
        "expected_risk_level": "SUSPICIOUS",
    },

    # C. High-Risk Scams
    {
        "id": "DEV_06",
        "category": "C. High-risk scams",
        "text": "Dad, I got into a terrible accident in Mumbai and I'm at the hospital! Please transfer ₹50,000 immediately to this doctor's UPI, don't tell mom!",
        "session_context": {"claimed_role": "family_member", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },
    {
        "id": "DEV_07",
        "category": "C. High-risk scams",
        "text": "Hello, this is SBI customer care. Your card is blocked. Please read out the 6-digit OTP sent to your phone right now to unblock.",
        "session_context": {"claimed_role": "bank", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },
    {
        "id": "DEV_08",
        "category": "C. High-risk scams",
        "text": "I am the CEO. I need you to execute an urgent wire transfer of ₹5,00,000 for a confidential acquisition. Do not discuss with anyone in the office.",
        "session_context": {"claimed_role": "executive", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # D. Benign Financial Requests
    {
        "id": "DEV_09",
        "category": "D. Benign financial requests",
        "text": "I need you to send ₹500 for dinner.",
        "session_context": {"claimed_role": "friend", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
    {
        "id": "DEV_10",
        "category": "D. Benign financial requests",
        "text": "Hi honey, can you transfer 2000 rupees to paying the monthly electric bill?",
        "session_context": {"claimed_role": "family_member", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # E. Benign Urgent Conversations
    {
        "id": "DEV_11",
        "category": "E. Benign urgent conversations",
        "text": "Hurry up, we are late for the flight! Please pack your bags right now!",
        "session_context": {"claimed_role": "family_member", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
    {
        "id": "DEV_12",
        "category": "E. Benign urgent conversations",
        "text": "Quick, submit the project proposal before the midnight deadline!",
        "session_context": {"claimed_role": "colleague", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # F. Benign OTP Discussions
    {
        "id": "DEV_13",
        "category": "F. Benign OTP discussions",
        "text": "Please send the OTP from your own phone to your own device.",
        "session_context": {"claimed_role": "system", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
    {
        "id": "DEV_14",
        "category": "F. Benign OTP discussions",
        "text": "Never share your bank OTP with anyone under any circumstances.",
        "session_context": {"claimed_role": "bank", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # G. Family Conversations (Paraphrase variations)
    {
        "id": "DEV_15",
        "category": "G. Family conversations",
        "text": "Mom called to ask if you can pick up milk on your way home.",
        "session_context": {"claimed_role": "family_member", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
    {
        "id": "DEV_16",
        "category": "G. Family conversations",
        "text": "Son, I am stranded on highway. Please send eighty thousand right away to doctor account, do not inform family.",
        "session_context": {"claimed_role": "family_member", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # H. Bank Conversations
    {
        "id": "DEV_17",
        "category": "H. Bank conversations",
        "text": "Good morning, this is HDFC Bank routine verification. Please confirm if your registered address is 101 MG Road.",
        "session_context": {"claimed_role": "bank", "identity_verified": False},
        "expected_risk_level": "SAFE",
    },
    {
        "id": "DEV_18",
        "category": "H. Bank conversations",
        "text": "This is bank fraud officer. Share your 4 digit UPI PIN immediately or account will be permanently blocked.",
        "session_context": {"claimed_role": "bank", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # I. Employer/CEO Conversations
    {
        "id": "DEV_19",
        "category": "I. Employer/CEO conversations",
        "text": "Please prepare the monthly financial balance sheet summary for our Monday team review.",
        "session_context": {"claimed_role": "executive", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
    {
        "id": "DEV_20",
        "category": "I. Employer/CEO conversations",
        "text": "I need you to authorize this payment urgently for vendor clearance. Keep it between us.",
        "session_context": {"claimed_role": "executive", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # J. Remote-Access Scenarios
    {
        "id": "DEV_21",
        "category": "J. Remote-access scenarios",
        "text": "Your computer has a virus. Download AnyDesk immediately and allow screen sharing access so tech support can fix it.",
        "session_context": {"claimed_role": "customer_support", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },
    {
        "id": "DEV_22",
        "category": "J. Remote-access scenarios",
        "text": "Install TeamViewer right now so IT support can inspect your corrupted system files under senior authorization.",
        "session_context": {"claimed_role": "customer_support", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # K. Digital-Arrest Style Scenarios
    {
        "id": "DEV_23",
        "category": "K. Digital-arrest style scenarios",
        "text": "This is Inspector Sharma from Delhi Cyber Crime. A legal warrant and CBI digital arrest has been issued against your Aadhaar card for money laundering. Do not disconnect this call!",
        "session_context": {"claimed_role": "police", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },
    {
        "id": "DEV_24",
        "category": "K. Digital-arrest style scenarios",
        "text": "Supreme Court order issued for illegal package. Police force dispatched unless you transfer money to safe account immediately.",
        "session_context": {"claimed_role": "police", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },

    # L. Delivery/Courier Scenarios
    {
        "id": "DEV_25",
        "category": "L. Delivery/courier scenarios",
        "text": "FedEx courier service: Your parcel containing illegal items has been seized by customs. Pay ₹15,000 customs penalty immediately or face arrest.",
        "session_context": {"claimed_role": "delivery_service", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },
    {
        "id": "DEV_26",
        "category": "L. Delivery/courier scenarios",
        "text": "DHL delivery update: Your package #8832 is out for delivery today between 2 PM and 5 PM.",
        "session_context": {"claimed_role": "delivery_service", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },

    # Additional Paraphrases & Edge Cases (DEV_27 - DEV_35)
    {
        "id": "DEV_27",
        "category": "Paraphrase: Money Transfer",
        "text": "Please make the payment now to this account right away.",
        "session_context": {"claimed_role": "unknown", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },
    {
        "id": "DEV_28",
        "category": "Paraphrase: Secrecy",
        "text": "Do not contact anyone else and send the money right now.",
        "session_context": {"claimed_role": "unknown", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },
    {
        "id": "DEV_29",
        "category": "Quoted Scam Example (Adversarial)",
        "text": "In our cybersecurity training, the professor said scammers often say: 'Give me your OTP immediately'.",
        "session_context": {"claimed_role": "teacher", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
    {
        "id": "DEV_30",
        "category": "Suspicious conversation without money request",
        "text": "I am watching you from across the street. Stay quiet.",
        "session_context": {"claimed_role": "unknown", "identity_verified": False},
        "expected_risk_level": "CAUTION",
    },
    {
        "id": "DEV_31",
        "category": "Unusable / Low Confidence Audio",
        "text": "",
        "voice_analysis": {"status": "insufficient_evidence", "reason": "unusable_audio"},
        "session_context": {"claimed_role": "unknown", "identity_verified": False},
        "expected_risk_level": "UNCERTAIN",
    },
    {
        "id": "DEV_32",
        "category": "Short Audio Abstention",
        "text": "",
        "voice_analysis": {"status": "insufficient_evidence", "reason": "audio_too_short"},
        "session_context": {"claimed_role": "unknown", "identity_verified": False},
        "expected_risk_level": "UNCERTAIN",
    },
    {
        "id": "DEV_33",
        "category": "Synthetic Voice + Harmless Text (Contradiction)",
        "text": "Hello, thank you for calling customer service. Have a great day!",
        "voice_analysis": {"status": "available", "synthetic_score": 0.95, "quality": "good"},
        "session_context": {"claimed_role": "customer_support", "identity_verified": False},
        "expected_risk_level": "CAUTION",
    },
    {
        "id": "DEV_34",
        "category": "Genuine Voice + High Risk Scam Text (Contradiction)",
        "text": "Transfer ₹80,000 immediately, do not tell anyone!",
        "voice_analysis": {"status": "available", "synthetic_score": 0.04, "quality": "good"},
        "session_context": {"claimed_role": "unknown", "identity_verified": False},
        "expected_risk_level": "HIGH_RISK",
    },
    {
        "id": "DEV_35",
        "category": "Educational cybersecurity discussion",
        "text": "Today we will discuss how phishing attacks use urgency and authority pressure to trick victims.",
        "session_context": {"claimed_role": "instructor", "identity_verified": True},
        "expected_risk_level": "SAFE",
    },
]

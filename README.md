# TrustShield
### Human-Centric Security & Verification Engine
TrustShield is a real-time security assistant built to help people
handle suspicious text messages and voice interactions more safely.

The main idea is simple:
**Pause. Verify. Stay Safe.**
Instead of depending on a single warning or keyword, TrustShield
looks at the wider context of an interaction and provides guidance
before a user takes a sensitive action.
---
## Why TrustShield?
Digital scams often rely on trust and urgency.
A caller may claim to be a bank employee, a message may say that an
account will be blocked, or a person may ask for an OTP, payment, or
other sensitive information.
In these situations, the difficult part is not only detecting that
something is suspicious. The user also needs to understand:
**"What should I do next?"**
TrustShield is designed to help at that point.
---
## What TrustShield Does
The current prototype supports both **text and voice interactions**.
It can:
- analyze conversation intent and context
- identify urgency and suspicious requests
- detect impersonation-related signals
- convert speech into text using Whisper
- analyze voice authenticity using AASIST-L
- verify claims and requested actions using trusted official sources
- combine multiple signals into a hybrid risk assessment
- track how risk changes across conversation turns
- provide clear safety guidance to the user
Examples of safety guidance include:
- **Verify First**
- **Pause the Action**
- **Withhold OTP**
The system provides evidence and guidance while keeping the final
decision with the user.
---
## How It Works
```text
Text / Voice Interaction
          ↓
Conversation Analysis
          ↓
Voice / Claim Verification
          ↓
Hybrid Risk Assessment
          ↓
Safety Guidance
          ↓
Safer User Decision

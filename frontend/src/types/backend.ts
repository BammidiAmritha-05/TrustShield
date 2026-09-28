export type InteractionType = 'voice' | 'text' | 'demo';
export type SessionStatus = 'created' | 'active' | 'ended';

export interface SessionResponse {
  session_id: string;
  status: SessionStatus;
  interaction_type: InteractionType;
  consent: boolean;
  created_at: string;
  ended_at: string | null;
  event_count: number;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  phase: number;
  ai_readiness: {
    transcription: string;
    voice_authenticity: string;
    conversation_intelligence: string;
    risk_engine: string;
    protection_agent: string;
    claim_verification: string;
  };
}

export type ProtectionLevel = 'SAFE' | 'CAUTION' | 'SUSPICIOUS' | 'HIGH_RISK' | 'UNCERTAIN';
export type RecommendedAction =
  | 'NO_ACTION_REQUIRED'
  | 'PAUSE_AND_VERIFY'
  | 'PAUSE_TRANSFER'
  | 'DO_NOT_SHARE_OTP'
  | 'STOP_AND_VERIFY'
  | 'VERIFY_INDEPENDENTLY'
  | 'STAY_AWARE';

export type ActionGateDecision =
  | 'ALLOW'
  | 'WARN'
  | 'PAUSE_AND_VERIFY'
  | 'BLOCK_AND_VERIFY'
  | 'HOLD_FOR_VERIFICATION';

export interface ActionGatePayload {
  status: string;
  gate_decision: ActionGateDecision;
  can_proceed: boolean;
  requires_verification: boolean;
  protection_level?: ProtectionLevel;
  recommended_action?: string | null;
  user_confirmation_required?: boolean;
  reason?: string;
  message?: string;
}

export interface RecoveryPayload {
  status: string;
  recovery_required: boolean;
  severity: string;
  title: string;
  action_type: string;
  protection_level: ProtectionLevel;
  gate_decision: ActionGateDecision;
  steps: string[];
  external_action_taken: boolean;
  loss_reversed: boolean;
  evidence_preservation_recommended: boolean;
}

export interface ProtectionUpdatePayload {
  status: string;
  protection_level?: ProtectionLevel;
  recommended_action?: string;
  verification_method?: string;
  why?: string;
  do?: string;
  do_not?: string;
  verify?: string;
  draft_verification_message?: string;
  confidence?: number;
  user_confirmation_required?: boolean;
  evidence_basis?: string[];
  reason?: string;
  message?: string;
}

export type RiskLevel = 'SAFE' | 'CAUTION' | 'SUSPICIOUS' | 'HIGH_RISK' | 'UNCERTAIN';

export interface SignalContribution {
  signal?: string;
  signal_name?: string;
  points?: number;
  weight?: number;
  value?: any;
  source?: string;
}

export interface TimelineTurn {
  turn_number?: number;
  turn_index?: number;
  risk_index?: number | null;
  risk_level?: RiskLevel | null;
  confidence?: number | null;
  timestamp?: string;
  instantaneous_risk?: number | null;
  temporal_risk?: number | null;
  cumulative_risk?: number | null;
  evidence_count?: number;
}

export interface PolicyViolation {
  policy_id: string;
  name: string;
  minimum_score?: number;
  minimum_level?: string;
  reason?: string;
}

export interface RiskUpdatePayload {
  status: string;
  risk_level?: RiskLevel;
  risk_index?: number;
  confidence?: number;
  contributing_signals?: SignalContribution[];
  evidence_trace?: any[];
  safety_policy_violations?: (string | PolicyViolation)[];
  temporal_timeline?: TimelineTurn[];
  explanation?: string;
  reason?: string;
  message?: string;
}

export interface SignalUpdatePayload {
  status: string;
  intent?: {
    type: string;
    confidence: number;
  };
  requested_action?: {
    type: string;
    sensitivity: string;
    confidence: number;
  };
  manipulation?: {
    urgency: number;
    secrecy: number;
    fear: number;
    authority_pressure: number;
    emotional_pressure: number;
    threat: number;
    reward: number;
    isolation: number;
    intimidation: number;
    forced_compliance: number;
  };
  impersonation?: {
    claimed_identity: string;
    possible_impersonation: boolean;
    confidence: number;
  };
  context?: {
    identity_verified: boolean;
    unusual_request: boolean;
    independent_verification_available: boolean;
  };
  explanation?: string;
  reason?: string;
  message?: string;
}

export type ClaimStatus = 'VERIFIED' | 'NOT_VERIFIED' | 'CONTRADICTED' | 'NO_CLAIM_DETECTED';

export interface ClaimItem {
  text: string;
  status: ClaimStatus;
  evidence?: string;
  confidence: number;
  evidence_origin: string;
  currentness: string;
}

export interface SourceInfo {
  url: string;
  authority: string;
  retrieved_at: string;
  relevance: string;
  tier: string;
  source_type: string;
  freshness: string;
  evidence_origin: string;
  http_status: number;
  content_length_bytes: number;
}

export interface ClaimVerificationPayload {
  status: string;
  entity?: {
    name: string;
    type: string;
    jurisdiction: string;
    ambiguity: boolean;
    status: ClaimStatus;
  };
  claims?: ClaimItem[];
  action?: {
    type: string;
    status: string;
  };
  sources?: SourceInfo[];
  verification?: {
    overall_status: ClaimStatus;
    confidence: number;
    otp_context: string;
  };
  limitations?: string[];
  reason?: string;
  message?: string;
}

export interface VoiceAnalysisPayload {
  status: string;
  synthetic_score?: number;
  bona_fide_score?: number;
  bona_fide_probability?: number;
  quality?: string;
  sample_count?: number;
  duration_seconds?: number;
  rms_energy?: number;
  spectral_flatness?: number;
  input_duration_sec?: number;
  reason?: string;
  message?: string;
}

export interface TranscriptPayload {
  text: string;
  duration?: number;
  language?: string;
  start?: number;
  end?: number;
}

export interface ErrorPayload {
  code: string;
  message: string;
}

export interface WSServerEvent {
  type: string;
  version: number;
  session_id: string;
  timestamp: string;
  payload: any;
}

export interface TranscriptMessage {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  text: string;
  timestamp: string;
  isFinal: boolean;
}

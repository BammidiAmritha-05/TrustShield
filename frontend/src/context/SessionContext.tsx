import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import {
  ClaimVerificationPayload,
  ErrorPayload,
  InteractionType,
  ProtectionUpdatePayload,
  RiskUpdatePayload,
  SessionResponse,
  SignalUpdatePayload,
  TimelineTurn,
  TranscriptMessage,
  VoiceAnalysisPayload,
  WSServerEvent,
} from '../types/backend';
import { createSession as apiCreateSession, endSession as apiEndSession, getSession as apiGetSession } from '../services/api';
import { TrustShieldWebSocketClient } from '../services/websocket';

interface SessionContextType {
  session: SessionResponse | null;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  connectionError: string | null;
  transcript: TranscriptMessage[];
  voiceAuthenticity: VoiceAnalysisPayload | null;
  signals: SignalUpdatePayload | null;
  risk: RiskUpdatePayload | null;
  claimVerification: ClaimVerificationPayload | null;
  protection: ProtectionUpdatePayload | null;
  timeline: TimelineTurn[];
  lastError: ErrorPayload | null;
  isRecording: boolean;

  startNewSession: (type: InteractionType, consent: boolean) => Promise<SessionResponse>;
  loadSession: (sessionId: string) => Promise<SessionResponse | null>;
  connectWebSocket: (sessionId: string) => void;
  sendTextMessage: (text: string) => boolean;
  sendAudioChunk: (buffer: ArrayBuffer) => boolean;
  flushUtterance: () => boolean;
  terminateSession: () => Promise<void>;
  resetSessionState: () => void;
  setIsRecording: (recording: boolean) => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([]);
  const [voiceAuthenticity, setVoiceAuthenticity] = useState<VoiceAnalysisPayload | null>(null);
  const [signals, setSignals] = useState<SignalUpdatePayload | null>(null);
  const [risk, setRisk] = useState<RiskUpdatePayload | null>(null);
  const [claimVerification, setClaimVerification] = useState<ClaimVerificationPayload | null>(null);
  const [protection, setProtection] = useState<ProtectionUpdatePayload | null>(null);
  const [timeline, setTimeline] = useState<TimelineTurn[]>([]);
  const [lastError, setLastError] = useState<ErrorPayload | null>(null);
  const [isRecording, setIsRecording] = useState<boolean>(false);

  const wsClientRef = useRef<TrustShieldWebSocketClient | null>(null);

  const resetSessionState = useCallback(() => {
    if (wsClientRef.current) {
      wsClientRef.current.disconnect();
      wsClientRef.current = null;
    }
    setSession(null);
    setConnectionStatus('disconnected');
    setConnectionError(null);
    setTranscript([]);
    setVoiceAuthenticity(null);
    setSignals(null);
    setRisk(null);
    setClaimVerification(null);
    setProtection(null);
    setTimeline([]);
    setLastError(null);
    setIsRecording(false);
  }, []);

  const handleServerEvent = useCallback((event: WSServerEvent) => {
    switch (event.type) {
      case 'SESSION_STARTED':
        setSession((prev) => (prev ? { ...prev, status: 'active' } : {
          session_id: event.session_id,
          status: 'active',
          interaction_type: 'text',
          consent: true,
          created_at: event.timestamp,
          ended_at: null,
          event_count: 1,
        }));
        break;

      case 'TEXT_RECEIVED':
        setTranscript((prev) => [
          ...prev,
          {
            id: `msg-${Date.now()}-${Math.random()}`,
            sender: 'user',
            text: event.payload.text || '',
            timestamp: event.timestamp,
            isFinal: true,
          },
        ]);
        break;

      case 'TRANSCRIPT_PARTIAL':
        setTranscript((prev) => {
          const filtered = prev.filter((m) => m.isFinal);
          return [
            ...filtered,
            {
              id: 'partial-live',
              sender: 'user',
              text: event.payload.text || '',
              timestamp: event.timestamp,
              isFinal: false,
            },
          ];
        });
        break;

      case 'TRANSCRIPT_FINAL':
        setTranscript((prev) => {
          const filtered = prev.filter((m) => m.id !== 'partial-live');
          return [
            ...filtered,
            {
              id: `msg-${Date.now()}-${Math.random()}`,
              sender: 'user',
              text: event.payload.text || '',
              timestamp: event.timestamp,
              isFinal: true,
            },
          ];
        });
        break;

      case 'VOICE_ANALYSIS':
        setVoiceAuthenticity(event.payload);
        break;

      case 'SIGNAL_UPDATE':
        setSignals(event.payload);
        break;

      case 'RISK_UPDATE':
        setRisk(event.payload);
        if (event.payload.temporal_timeline) {
          setTimeline(event.payload.temporal_timeline);
        }
        break;

      case 'CLAIM_VERIFICATION':
        setClaimVerification(event.payload);
        break;

      case 'PROTECTION_UPDATE':
        setProtection(event.payload);
        break;

      case 'ERROR':
        setLastError(event.payload);
        break;

      case 'SESSION_ENDED':
        setSession((prev) => (prev ? { ...prev, status: 'ended' } : null));
        setConnectionStatus('disconnected');
        break;

      default:
        break;
    }
  }, []);

  const connectWebSocket = useCallback(
    (sessionId: string) => {
      if (wsClientRef.current) {
        wsClientRef.current.disconnect();
      }

      const client = new TrustShieldWebSocketClient(
        sessionId,
        handleServerEvent,
        (status, err) => {
          setConnectionStatus(status);
          setConnectionError(err || null);
        }
      );

      wsClientRef.current = client;
      client.connect();
    },
    [handleServerEvent]
  );

  const startNewSession = useCallback(
    async (type: InteractionType, consent: boolean) => {
      resetSessionState();
      const newSession = await apiCreateSession(type, consent);
      setSession(newSession);
      return newSession;
    },
    [resetSessionState]
  );

  const loadSession = useCallback(
    async (sessionId: string): Promise<SessionResponse | null> => {
      try {
        const fetchedSession = await apiGetSession(sessionId);
        setSession(fetchedSession);
        return fetchedSession;
      } catch (err: any) {
        setConnectionError(`Session #${sessionId} could not be found or is unavailable.`);
        return null;
      }
    },
    []
  );

  const sendTextMessage = useCallback((text: string): boolean => {
    if (wsClientRef.current) {
      return wsClientRef.current.sendText(text);
    }
    return false;
  }, []);

  const sendAudioChunk = useCallback((buffer: ArrayBuffer): boolean => {
    if (wsClientRef.current) {
      return wsClientRef.current.sendAudioChunk(buffer);
    }
    return false;
  }, []);

  const flushUtterance = useCallback((): boolean => {
    if (wsClientRef.current) {
      return wsClientRef.current.flushUtterance();
    }
    return false;
  }, []);

  const terminateSession = useCallback(async () => {
    if (wsClientRef.current) {
      wsClientRef.current.stopSession();
      wsClientRef.current.disconnect();
      wsClientRef.current = null;
    }
    if (session) {
      try {
        const ended = await apiEndSession(session.session_id);
        setSession(ended);
      } catch (e) {
        setSession((prev) => (prev ? { ...prev, status: 'ended' } : null));
      }
    }
    setConnectionStatus('disconnected');
  }, [session]);

  return (
    <SessionContext.Provider
      value={{
        session,
        connectionStatus,
        connectionError,
        transcript,
        voiceAuthenticity,
        signals,
        risk,
        claimVerification,
        protection,
        timeline,
        lastError,
        isRecording,
        startNewSession,
        loadSession,
        connectWebSocket,
        sendTextMessage,
        sendAudioChunk,
        flushUtterance,
        terminateSession,
        resetSessionState,
        setIsRecording,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

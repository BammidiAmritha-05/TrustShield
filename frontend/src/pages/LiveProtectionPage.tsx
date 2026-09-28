import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSession } from '../context/SessionContext';
import { ProtectionBanner } from '../components/ProtectionBanner';
import { RiskGauge } from '../components/RiskGauge';
import { VoiceAuthenticityCard } from '../components/VoiceAuthenticityCard';
import { ConversationSignals } from '../components/ConversationSignals';
import { ClaimVerificationCard } from '../components/ClaimVerificationCard';
import { ActionGuidance } from '../components/ActionGuidance';
import { EvidenceTimeline } from '../components/EvidenceTimeline';
import { TranscriptFeed } from '../components/TranscriptFeed';
import { Shield, Clock, Power, AlertCircle, Wifi, WifiOff } from 'lucide-react';
import { PcmWavRecorder } from '../utils/pcm_recorder';

export const LiveProtectionPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const {
    session,
    connectionStatus,
    connectionError,
    transcript,
    voiceAuthenticity,
    signals,
    risk,
    claimVerification,
    protection,
    actionGate,
    recovery,
    timeline,
    lastError,
    isRecording,
    loadSession,
    connectWebSocket,
    sendTextMessage,
    sendAudioChunk,
    flushUtterance,
    terminateSession,
    setIsRecording,
  } = useSession();

  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);
  const [sessionNotFound, setSessionNotFound] = useState<boolean>(false);
  const pcmRecorderRef = useRef<PcmWavRecorder | null>(null);

  // Connect WS & fetch session metadata if loaded directly from URL
  useEffect(() => {
    if (!sessionId) return;

    let isMounted = true;

    // Fetch session details from REST if not in context
    if (!session || session.session_id !== sessionId) {
      loadSession(sessionId).then((loaded) => {
        if (!isMounted) return;
        if (!loaded) {
          setSessionNotFound(true);
        } else {
          setSessionNotFound(false);
          connectWebSocket(sessionId);
        }
      });
    } else {
      // Session exists in context, ensure WebSocket connects
      connectWebSocket(sessionId);
    }

    return () => {
      isMounted = false;
    };
  }, [sessionId]);

  // Session Duration Counter & Cleanup
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => {
      clearInterval(timer);
      if (pcmRecorderRef.current) {
        pcmRecorderRef.current.stop();
        pcmRecorderRef.current = null;
      }
    };
  }, []);

  const formatDuration = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleEndSession = async () => {
    if (pcmRecorderRef.current && isRecording) {
      pcmRecorderRef.current.stop();
      pcmRecorderRef.current = null;
      setIsRecording(false);
      flushUtterance();
    }
    await terminateSession();
    if (sessionId) {
      navigate(`/session/${sessionId}/summary`);
    }
  };

  // Microphone Audio Recorder Handler using Web Audio API PCM WAV streaming
  const toggleRecording = async () => {
    if (isRecording) {
      if (pcmRecorderRef.current) {
        pcmRecorderRef.current.stop();
        pcmRecorderRef.current = null;
      }
      setIsRecording(false);
      flushUtterance();
    } else {
      try {
        const recorder = new PcmWavRecorder({
          sampleRate: 16000,
          timeSliceMs: 1000,
          onAudioChunk: (chunk: ArrayBuffer) => {
            sendAudioChunk(chunk);
          },
          onError: (err: Error) => {
            console.error('Audio streaming error:', err);
            setIsRecording(false);
          },
        });

        pcmRecorderRef.current = recorder;
        await recorder.start();
        setIsRecording(true);
      } catch (err: any) {
        console.error('Microphone stream initialization error:', err);
        setIsRecording(false);
      }
    }
  };

  if (sessionNotFound) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
          <div className="w-14 h-14 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 mx-auto mb-6">
            <AlertCircle className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">
            Protection Session Not Found
          </h2>
          <p className="text-sm text-slate-400 mb-6 leading-relaxed">
            Session <span className="font-mono text-slate-300">#{sessionId}</span> is not active or has expired. All protection sessions are evaluated in-memory and require an active session ID.
          </p>
          <button
            onClick={() => navigate('/')}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-semibold text-sm transition-colors inline-flex items-center gap-2"
          >
            Start New Session
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-8 space-y-4 sm:space-y-6">
      {/* Session Controls Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl sm:rounded-2xl p-3.5 sm:p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 flex-shrink-0">
            <Shield className="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-slate-100 text-xs sm:text-sm truncate">Session #{sessionId?.slice(0, 8)}</span>
              <span className="text-[9px] sm:text-[10px] px-1.5 sm:px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 font-semibold border border-teal-500/20 uppercase">
                {session?.interaction_type || 'Voice/Text'} Mode
              </span>
            </div>
            <div className="flex items-center gap-2 sm:gap-3 text-[11px] sm:text-xs text-slate-400 mt-0.5">
              <span className="flex items-center gap-1 font-mono">
                <Clock className="w-3 h-3 sm:w-3.5 sm:h-3.5" /> {formatDuration(elapsedSeconds)}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                {connectionStatus === 'connected' ? (
                  <span className="text-emerald-400 flex items-center gap-1 font-semibold">
                    <Wifi className="w-3 h-3 sm:w-3.5 sm:h-3.5" /> Connected
                  </span>
                ) : (
                  <span className="text-amber-400 flex items-center gap-1 font-semibold">
                    <WifiOff className="w-3 h-3 sm:w-3.5 sm:h-3.5" /> {connectionStatus.toUpperCase()}
                  </span>
                )}
              </span>
            </div>
          </div>
        </div>

        <button
          onClick={handleEndSession}
          className="w-full sm:w-auto bg-rose-600 hover:bg-rose-500 text-white px-3.5 sm:px-4 py-2 sm:py-2.5 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-rose-900/20"
        >
          <Power className="w-3.5 h-3.5 sm:w-4 sm:h-4" /> End Session & Review Summary
        </button>
      </div>

      {/* Error Alert Banner */}
      {(lastError || connectionError) && (
        <div className="bg-rose-950/80 border border-rose-600/60 p-3 sm:p-4 rounded-xl sm:rounded-2xl text-rose-100 text-xs flex items-center gap-2.5 sm:gap-3">
          <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 text-rose-400 flex-shrink-0" />
          <div className="min-w-0">
            <span className="font-bold block">Session Warning:</span>
            <span className="break-words">{lastError?.message || connectionError}</span>
          </div>
        </div>
      )}

      {/* PRIMARY DYNAMIC PROTECTION BANNER */}
      <ProtectionBanner protection={protection} />

      {/* GRID LAYOUT: Mobile Stack (1-Col) / Desktop Multi-Column (3-Col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* LEFT COLUMN: Transcript & Action Guidance */}
        <div className="lg:col-span-2 space-y-4 sm:space-y-6">
          <TranscriptFeed
            transcript={transcript}
            interactionType={session?.interaction_type || 'text'}
            onSendText={sendTextMessage}
            isRecording={isRecording}
            onToggleRecording={toggleRecording}
          />

          <ActionGuidance 
            protection={protection}
            actionGate={actionGate}
            recovery={recovery}
          />

          <ConversationSignals signals={signals} />

          <ClaimVerificationCard claim={claimVerification} />
        </div>

        {/* RIGHT COLUMN: Risk Engine & Voice Authenticity & Timeline */}
        <div className="space-y-4 sm:space-y-6">
          <RiskGauge risk={risk} />

          <VoiceAuthenticityCard voice={voiceAuthenticity} />

          <EvidenceTimeline timeline={timeline} />
        </div>
      </div>
    </div>
  );
};

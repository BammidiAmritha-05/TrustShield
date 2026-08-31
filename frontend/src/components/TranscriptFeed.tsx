import React, { useState } from 'react';
import { TranscriptMessage } from '../types/backend';
import { Send, Mic, MicOff, MessageSquare, User, Bot, Loader2 } from 'lucide-react';

interface TranscriptFeedProps {
  transcript: TranscriptMessage[];
  interactionType: string;
  onSendText: (text: string) => void;
  isRecording?: boolean;
  onToggleRecording?: () => void;
}

export const TranscriptFeed: React.FC<TranscriptFeedProps> = ({
  transcript,
  interactionType,
  onSendText,
  isRecording = false,
  onToggleRecording,
}) => {
  const [inputText, setInputText] = useState<string>('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSendText(inputText.trim());
    setInputText('');
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col h-[500px]">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4 flex-shrink-0">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold text-slate-100">Live Conversation Stream</h3>
        </div>
        <span className="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-400 font-mono">
          {interactionType === 'voice' ? 'Voice Streaming' : 'Text Input'}
        </span>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-2 mb-4">
        {transcript.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-500 text-xs text-center p-4">
            No conversation messages received yet. Send a text message or stream audio to begin real-time safety evaluation.
          </div>
        ) : (
          transcript.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-start' : 'justify-end'}`}
            >
              <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 flex-shrink-0 mt-0.5">
                <User className="w-4 h-4" />
              </div>
              <div
                className={`p-3 rounded-2xl max-w-[85%] text-xs ${
                  msg.isFinal
                    ? 'bg-slate-950 border border-slate-800 text-slate-200'
                    : 'bg-indigo-950/40 border border-indigo-500/30 text-indigo-200 italic animate-pulse'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1 gap-2">
                  <span className="font-semibold text-slate-400">Incoming Message</span>
                  <span>{msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : 'Just now'}</span>
                </div>
                <p className="leading-relaxed">{msg.text}</p>
                {!msg.isFinal && <span className="text-[10px] text-indigo-400 block mt-1">Processing live transcript...</span>}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Input Composer */}
      {interactionType === 'text' || interactionType === 'demo' ? (
        <form onSubmit={handleSend} className="flex gap-2 flex-shrink-0">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type or paste a suspicious message to analyze..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
          <button
            type="submit"
            disabled={!inputText.trim()}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-4 py-2.5 rounded-xl font-semibold text-xs flex items-center gap-1.5 transition-colors flex-shrink-0"
          >
            <Send className="w-4 h-4" /> Send
          </button>
        </form>
      ) : (
        <div className="flex items-center justify-between bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-400 flex-shrink-0">
          <span>Voice Audio Stream Active</span>
          {onToggleRecording && (
            <button
              onClick={onToggleRecording}
              className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-colors ${
                isRecording
                  ? 'bg-rose-600 text-white hover:bg-rose-500'
                  : 'bg-indigo-600 text-white hover:bg-indigo-500'
              }`}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              {isRecording ? 'Stop Mic Stream' : 'Start Mic Stream'}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

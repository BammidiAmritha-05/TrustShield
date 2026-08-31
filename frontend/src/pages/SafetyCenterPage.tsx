import React from 'react';
import { Shield, Key, AlertTriangle, PhoneCall, Lock, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const SafetyCenterPage: React.FC = () => {
  const safetyGuidelines = [
    {
      icon: <Key className="w-5 h-5 text-amber-400" />,
      title: 'Never Share One-Time Passwords (OTP)',
      summary: 'Banks, government entities, and official payment platforms will never call or message asking you to read or share your OTP.',
      doText: 'Keep OTP private and enter it only on verified banking applications you directly initiated.',
      dontText: 'Never read out OTP over a phone call, WhatsApp chat, or online web form sent via SMS.',
    },
    {
      icon: <PhoneCall className="w-5 h-5 text-sky-400" />,
      title: 'Caller Identity vs Claimed Authority',
      summary: 'Scammers frequently impersonate bank managers, police officials, courier agents, or family members using synthetic audio or spoofed IDs.',
      doText: 'Hang up and independently dial the official customer care number listed on your physical card or official website.',
      dontText: 'Do not trust incoming caller ID  names or urgent identity claims without independent verification.',
    },
    {
      icon: <AlertTriangle className="w-5 h-5 text-rose-400" />,
      title: 'Urgency & Pressure Tactics',
      summary: 'Fraudsters create artificial deadlines (e.g. "Account blocked in 10 minutes", "Arrest warrant issued") to force compliance before you can think.',
      doText: 'Take a deep breath and pause. Legitimate organizations allow reasonable time to verify and resolve issues.',
      dontText: 'Never make rushed transfers or download screen-sharing APKs under pressure.',
    },
    {
      icon: <Lock className="w-5 h-5 text-teal-400" />,
      title: 'Fee Payment to Claim Subsidies/Prizes',
      summary: 'Government welfare schemes (e.g. PM Kisan, Rythu Bharosa) never demand an upfront "processing fee" or "unlock charge".',
      doText: 'Check your official welfare portal directly or visit your local administrative office in person.',
      dontText: 'Never pay advance registration or clearance fees to receive a government grant or lottery prize.',
    },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto px-3 sm:px-4 py-6 sm:py-10 space-y-6 sm:space-y-10">
      <div className="border-b border-slate-800 pb-4 sm:pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-300 text-[11px] sm:text-xs font-semibold mb-3">
          <Shield className="w-3.5 h-3.5" /> TrustShield Safety Center
        </div>
        <h1 className="text-xl sm:text-3xl font-bold text-white mb-2">Practical Security Guidance</h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-2xl leading-relaxed">
          Essential rules to protect yourself against voice cloning, urgent financial coercion, and impersonation scams.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5">
        {safetyGuidelines.map((guide, idx) => (
          <div key={idx} className="bg-slate-900/80 border border-slate-800 rounded-xl sm:rounded-2xl p-4 sm:p-5 flex flex-col justify-between shadow-sm">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center flex-shrink-0">
                  {guide.icon}
                </div>
                <h3 className="font-bold text-white text-sm">{guide.title}</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">{guide.summary}</p>
            </div>
            <div className="space-y-2 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-[11px] sm:text-xs">
              <div className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold font-mono flex-shrink-0">DO:</span>
                <span className="text-slate-300">{guide.doText}</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-rose-400 font-bold font-mono flex-shrink-0">DON'T:</span>
                <span className="text-slate-400">{guide.dontText}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-slate-900 border border-teal-500/20 rounded-2xl sm:rounded-3xl p-5 sm:p-8 flex flex-col sm:flex-row items-center justify-between gap-4 sm:gap-6">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-white mb-1">Have a suspicious message or call?</h3>
          <p className="text-xs text-slate-400 max-w-md leading-relaxed">
            Start a live TrustShield session now to evaluate voice authenticity, detect coercion tactics, and verify official claims in real-time.
          </p>
        </div>
        <Link
          to="/"
          className="w-full sm:w-auto px-4 sm:px-5 py-2.5 sm:py-3 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-lg shadow-teal-900/20 flex items-center justify-center gap-2 whitespace-nowrap transition-all"
        >
          Start Protection <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};

import React from 'react';
import { ClaimVerificationPayload, ClaimStatus } from '../types/backend';
import { FileCheck, ExternalLink, AlertOctagon, CheckCircle2, XCircle, HelpCircle } from 'lucide-react';

interface ClaimVerificationCardProps {
  claim: ClaimVerificationPayload | null;
}

export const ClaimVerificationCard: React.FC<ClaimVerificationCardProps> = ({ claim }) => {
  if (!claim || claim.status !== 'available') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-slate-400">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-slate-200 flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-emerald-400" /> Official Source Verification
          </h3>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">Registry Ready</span>
        </div>
        <p className="text-xs text-slate-400">
          Official claim verification engine ready. Extracts factual scheme/banking claims and verifies against Tier-1 official registries (.gov.in, bank.sbi).
        </p>
      </div>
    );
  }

  const overallStatus: ClaimStatus = claim.verification?.overall_status || 'NO_CLAIM_DETECTED';

  const getStatusBadge = (st: ClaimStatus) => {
    switch (st) {
      case 'VERIFIED':
        return (
          <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> OFFICIAL POLICY ALIGNMENT
          </span>
        );
      case 'CONTRADICTED':
        return (
          <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center gap-1">
            <XCircle className="w-3.5 h-3.5" /> OFFICIAL POLICY CONTRADICTION
          </span>
        );
      case 'NOT_VERIFIED':
        return (
          <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
            <HelpCircle className="w-3.5 h-3.5" /> NOT VERIFIED (UNAVAILABLE)
          </span>
        );
      case 'NO_CLAIM_DETECTED':
      default:
        return (
          <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-800 text-slate-400 border border-slate-700">
            NO CLAIM DETECTED
          </span>
        );
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <FileCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="font-semibold text-slate-100">Official Claim & Source Verification</h3>
        </div>
        {getStatusBadge(overallStatus)}
      </div>

      {/* Entity & Action 3D Breakdown */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        {/* Entity Info */}
        {claim.entity && claim.entity.name !== 'None' ? (
          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs">
            <div className="flex justify-between items-center mb-1">
              <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Extracted Entity</span>
              <span className="text-slate-400">Jurisdiction: <strong className="text-slate-200">{claim.entity.jurisdiction}</strong></span>
            </div>
            <div className="flex justify-between items-center">
              <p className="text-sm font-bold text-white">{claim.entity.name}</p>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                claim.entity.status === 'VERIFIED'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : claim.entity.status === 'CONTRADICTED'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
              }`}>
                {claim.entity.status}
              </span>
            </div>
          </div>
        ) : null}

        {/* Action Info */}
        {claim.action && claim.action.type !== 'none' ? (
          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs">
            <div className="flex justify-between items-center mb-1">
              <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Requested Action</span>
              <span className="text-slate-400">Type: <strong className="text-slate-200">{claim.action.type.replace(/_/g, ' ')}</strong></span>
            </div>
            <div className="flex justify-between items-center">
              <p className="text-sm font-bold text-white capitalize">{claim.action.type.replace(/_/g, ' ')}</p>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                claim.action.status === 'SUPPORTED'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : claim.action.status === 'CONTRADICTED'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
              }`}>
                {claim.action.status}
              </span>
            </div>
          </div>
        ) : null}
      </div>

      {/* Claims List */}
      {claim.claims && claim.claims.length > 0 && (
        <div className="mb-4 space-y-2">
          <span className="text-xs font-semibold text-slate-400 block">Analyzed Claim Items</span>
          {claim.claims.map((c, idx) => (
            <div key={idx} className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs">
              <div className="flex justify-between items-start gap-2 mb-1">
                <p className="text-slate-200 font-medium">{c.text}</p>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                    c.status === 'CONTRADICTED'
                      ? 'bg-rose-500/20 text-rose-300'
                      : c.status === 'VERIFIED'
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : 'bg-amber-500/20 text-amber-300'
                  }`}
                >
                  {c.status}
                </span>
              </div>
              {c.evidence && <p className="text-slate-400 mt-1 italic">{c.evidence}</p>}
            </div>
          ))}
        </div>
      )}

      {/* Authoritative Sources */}
      {claim.sources && claim.sources.length > 0 && (
        <div className="mb-4 space-y-2">
          <span className="text-xs font-semibold text-slate-400 block">Tier-1 Authoritative Official Source</span>
          {claim.sources.map((src, idx) => (
            <div key={idx} className="bg-emerald-950/20 border border-emerald-500/30 p-3 rounded-xl text-xs">
              <div className="flex justify-between items-center mb-1">
                <span className="font-semibold text-emerald-300">{src.authority}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">
                  {src.tier}
                </span>
              </div>
              <a
                href={src.url}
                target="_blank"
                rel="noreferrer"
                className="text-sky-400 hover:underline flex items-center gap-1 font-mono text-[11px] mb-1"
              >
                {src.url} <ExternalLink className="w-3 h-3" />
              </a>
              <p className="text-slate-300 text-[11px]">{src.relevance}</p>
              <div className="flex justify-between text-[10px] text-slate-500 mt-2 font-mono">
                <span>Origin: {src.evidence_origin}</span>
                <span>Retrieved: {src.retrieved_at ? new Date(src.retrieved_at).toLocaleTimeString() : 'Unknown'}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Audit Limitations */}
      {claim.limitations && claim.limitations.length > 0 && (
        <div className="text-[11px] bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-slate-400">
          <span className="font-semibold text-slate-300 block mb-1">Verification Audit Limitations:</span>
          <ul className="list-disc list-inside space-y-0.5">
            {claim.limitations.map((lim, idx) => (
              <li key={idx}>{lim}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
